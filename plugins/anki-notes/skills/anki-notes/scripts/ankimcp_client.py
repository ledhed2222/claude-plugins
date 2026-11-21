# pyright: basic
"""Minimal asyncio client for the AnkiMCP add-on's HTTP server (MCP over HTTP).

Standard library only (Python 3.9+): a raw HTTP/1.1 POST over
asyncio.open_connection, one connection per request ("Connection: close"),
handling chunked bodies and single-event SSE responses. Calls are made one at a
time on purpose: they all write into one Anki collection.

    async with Client() as anki:
        decks = await anki.call("list_decks")
"""
import asyncio
import json

HOST, PORT = "127.0.0.1", 3141
TIMEOUT = 300
SYNC_POLLS = 120


class AnkiError(Exception):
    pass


def _dechunk(body):
    out, rest = b"", body
    while rest:
        size_line, _, rest = rest.partition(b"\r\n")
        size = int(size_line.split(b";")[0], 16)
        if size == 0:
            break
        out, rest = out + rest[:size], rest[size + 2:]
    return out


def parse_response(raw):
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split()[1])
    headers = {k.strip().lower(): v.strip() for k, _, v in (l.partition(":") for l in lines[1:])}
    if "chunked" in headers.get("transfer-encoding", "").lower():
        body = _dechunk(body)
    text = body.decode()
    for line in text.splitlines():  # SSE: the JSON-RPC message is the last data: line
        if line.startswith("data:"):
            text = line[5:]
    return status, headers, (json.loads(text) if text.strip() else None)


class Client:
    def __init__(self, host=HOST, port=PORT):
        self.host, self.port = host, port
        self.session = None
        self.n = 0

    async def _post(self, message):
        data = json.dumps(message).encode()
        head = [
            "POST / HTTP/1.1",
            f"Host: {self.host}:{self.port}",
            "Content-Type: application/json",
            "Accept: application/json, text/event-stream",
            f"Content-Length: {len(data)}",
            "Connection: close",
        ]
        if self.session:
            head.append(f"Mcp-Session-Id: {self.session}")
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), TIMEOUT)
        except OSError as e:
            raise AnkiError(f"AnkiMCP add-on unreachable at {self.host}:{self.port}"
                            f" (is Anki open with the add-on installed?): {e}") from None
        try:
            writer.write(("\r\n".join(head) + "\r\n\r\n").encode() + data)
            await writer.drain()
            raw = await asyncio.wait_for(reader.read(), TIMEOUT)  # Connection: close, so read to EOF
        finally:
            writer.close()
            await writer.wait_closed()
        status, headers, payload = parse_response(raw)
        if status >= 400:
            raise AnkiError(f"HTTP {status}")
        self.session = headers.get("mcp-session-id") or self.session
        return payload

    async def __aenter__(self):
        r = await self._post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "anki-notes", "version": "1"}}})
        if r is None or "error" in r:
            raise AnkiError(f"MCP initialize failed: {r and r.get('error')}")
        await self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return self

    async def __aexit__(self, *exc):
        return False

    async def call(self, tool, **args):
        self.n += 1
        r = await self._post({"jsonrpc": "2.0", "id": self.n, "method": "tools/call",
                              "params": {"name": tool, "arguments": args}})
        if r is None:
            raise AnkiError(f"{tool}: empty response")
        if "error" in r:
            raise AnkiError(f"{tool}: {r['error']}")
        res = r["result"]
        if res.get("isError"):
            raise AnkiError(f"{tool}: {res['content'][0]['text']}")
        return res.get("structuredContent") or json.loads(res["content"][0]["text"])

    async def sync(self, poll=1.0):
        """Sync to AnkiWeb and wait for success. A conflict is cancelled, never resolved."""
        job = (await self.call("sync"))["job_id"]
        for _ in range(SYNC_POLLS):
            s = await self.call("sync", job_id=job)
            if s["status"] == "conflict":
                # never pick a side: the wrong direction discards one side's changes
                await self.call("sync", job_id=job, resolve="cancel")
                raise AnkiError("sync: AnkiWeb needs a full sync; cancelled. Resolve it in Anki, choosing which side to keep.")
            if s["status"] != "running":
                if s["status"] != "success":
                    raise AnkiError(f"sync: {s['status']} {s.get('error') or ''}")
                return s
            await asyncio.sleep(poll)
        raise AnkiError(f"sync: still running after {SYNC_POLLS} polls; check Anki")


async def read_json(path, missing=None):
    """missing: returned when the file doesn't exist; None means raise."""
    def _read():
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            if missing is None:
                raise
            return missing
    return await asyncio.to_thread(_read)


async def write_text(path, text):
    def _write():
        with open(path, "w") as f:
            f.write(text)
    await asyncio.to_thread(_write)
