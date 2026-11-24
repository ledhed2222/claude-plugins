"""The rules that keep local and remote tested alike (see both_servers.py)."""
import importlib
import inspect
import re
import unittest

from both_servers import DATA, HERE, OPERATIONS, SERVERS, UNVERIFIED, check_args, path, tools
from replies import LOCAL, REMOTE

_SKILL = HERE.parent / "SKILL.md"


class FixturePairTests(unittest.TestCase):
    def test_every_shared_operation_has_both_fixtures(self):
        for op in OPERATIONS["shared"]:
            for server in SERVERS:
                self.assertTrue(path(server, op).exists(), f"{server}/{op}.json is missing")

    def test_every_fixture_is_listed(self):
        for server in SERVERS:
            listed = set(OPERATIONS["shared"]) | set(OPERATIONS["only"].get(server, {}))
            on_disk = {p.stem for p in (DATA / server).glob("*.json")}
            self.assertEqual(on_disk - listed, set(), f"{server} fixtures not in operations.json")

    def test_fixture_tools_exist_on_their_server(self):
        for server in SERVERS:
            known = set(tools(server)) | UNVERIFIED[server]
            named = [t[server] for t in OPERATIONS["shared"].values()] + list(OPERATIONS["only"].get(server, {}).values())
            self.assertEqual(sorted(set(named) - known), [], f"{server} tools in operations.json missing from its _tools.json")


class ContractPairTests(unittest.TestCase):
    def test_every_contract_runs_on_both_servers(self):
        for f in sorted(HERE.glob("test_*.py")):
            module = importlib.import_module(f.stem)
            classes = [c for _, c in inspect.getmembers(module, inspect.isclass) if c.__module__ == module.__name__]
            for contract in (c for c in classes if c.__name__.endswith("Contract")):
                servers = sorted(c.server for c in classes if issubclass(c, contract) and issubclass(c, unittest.TestCase))
                self.assertEqual(servers, sorted(SERVERS), f"{f.stem}.{contract.__name__} must run as a Local and a Remote class")

    def test_no_server_test_outside_a_contract(self):
        """A TestCase pinned to one server must come from a Contract, so its twin exists."""
        for f in sorted(HERE.glob("test_*.py")):
            module = importlib.import_module(f.stem)
            for _, c in inspect.getmembers(module, inspect.isclass):
                if c.__module__ == module.__name__ and issubclass(c, unittest.TestCase) and getattr(c, "server", None):
                    self.assertTrue(any(b.__name__.endswith("Contract") for b in c.__mro__), f"{f.stem}.{c.__name__}")


class ToolNameTests(unittest.TestCase):
    def test_skill_table_names_real_tools(self):
        """Each row of SKILL.md's "Anki tools" table starts each column with a tool of that server, and never names the other's."""
        text = _SKILL.read_text()
        table = text[text.index("| Operation |"):].split("\n\n", 1)[0].splitlines()[2:]
        self.assertGreater(len(table), 5)
        both = {LOCAL: set(tools(LOCAL)) | UNVERIFIED[LOCAL], REMOTE: set(tools(REMOTE))}
        for line in table:
            op, *cells = [c.strip() for c in line.strip().strip("|").split("|")]
            self.assertEqual(len(cells), 2, line)
            for server, other, cell in ((LOCAL, REMOTE, cells[0]), (REMOTE, LOCAL, cells[1])):
                tokens = re.findall(r"`([a-z_]+)", cell)
                self.assertIn(tokens[0], both[server], f"{op}: the {server} column must start with a {server} tool")
                wrong = [t for t in tokens if t in both[other] and t not in both[server]]
                self.assertEqual(wrong, [], f"{op}: the {server} column names {other} tools")

    def test_scripts_only_call_tools_their_server_has(self):
        for f in sorted(HERE.glob("*.py")):
            if f.name.startswith("test_"):
                continue
            for name in re.findall(r'call\("([a-z_]+)"', f.read_text()):
                server = REMOTE if name.startswith("anki_") else LOCAL
                self.assertIn(name, set(tools(server)) | UNVERIFIED[server], f"{f.name} calls {name}")

    def test_unverified_tools_are_few_and_named(self):
        self.assertLessEqual(len(UNVERIFIED[LOCAL]), 2)
        self.assertEqual(UNVERIFIED[REMOTE], set())


class SchemaCheckTests(unittest.TestCase):
    """check_call is what every planner contract leans on, so test the checker itself."""

    def test_catches_missing_unknown_and_mistyped(self):
        schema = tools(REMOTE)["anki_notes_create"]["inputSchema"]
        self.assertEqual(check_args({"deck_id": 1, "note_type_id": 2, "fields": {"Front": "Q"}}, schema), [])
        self.assertIn("missing required 'fields'", check_args({"deck_id": 1, "note_type_id": 2}, schema))
        self.assertIn("unknown argument 'deck_name'", check_args({"deck_id": 1, "note_type_id": 2, "fields": {}, "deck_name": "x"}, schema))
        self.assertTrue(any("deck_id" in p for p in check_args({"deck_id": "AI", "note_type_id": 2, "fields": {}}, schema)))
        local = tools(LOCAL)["tag_add"]["inputSchema"]
        self.assertTrue(any("tags" in p for p in check_args({"note_ids": [1], "tags": ["a"]}, local)))  # the add-on wants a string


if __name__ == "__main__":
    unittest.main()
