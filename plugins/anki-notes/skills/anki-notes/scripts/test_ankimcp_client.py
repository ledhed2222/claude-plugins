import asyncio
import json
import unittest

from ankimcp_client import AnkiError, Client, parse_response


async def fake_server(replies, seen):
    """A one-shot-per-request HTTP server that answers like the add-on (SSE, chunked)."""
    async def handle(reader, writer):
        head = await reader.readuntil(b"\r\n\r\n")
        length = int([l for l in head.decode().split("\r\n") if l.lower().startswith("content-length")][0].split(":")[1])
        msg = json.loads(await reader.readexactly(length))
        seen.append((head.decode(), msg))
        result = replies(msg)
        body = b"" if result is None else f"event: message\ndata: {json.dumps(result)}\n\n".encode()
        chunked = f"{len(body):x}\r\n".encode() + body + b"\r\n0\r\n\r\n" if body else b"0\r\n\r\n"
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nMcp-Session-Id: abc\r\n"
                     b"Transfer-Encoding: chunked\r\n\r\n" + chunked)
        await writer.drain()
        writer.close()
    return await asyncio.start_server(handle, "127.0.0.1", 0)


def tool_result(payload, error=False):
    return {"result": {"isError": error, "content": [{"type": "text", "text": json.dumps(payload) if not error else payload}]}}


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def run_with(self, replies):
        seen = []
        server = await fake_server(replies, seen)
        port = server.sockets[0].getsockname()[1]
        return server, Client(port=port), seen

    async def test_call_round_trip_and_session(self):
        def replies(msg):
            if msg.get("method") == "initialize":
                return {"jsonrpc": "2.0", "id": 0, "result": {}}
            if msg.get("method") == "tools/call":
                return dict(tool_result({"decks": ["Default"]}), jsonrpc="2.0", id=msg["id"])
            return None
        server, client, seen = await self.run_with(replies)
        async with server:
            async with client as anki:
                self.assertEqual(await anki.call("list_decks"), {"decks": ["Default"]})
        self.assertIn("Mcp-Session-Id: abc", seen[-1][0])

    async def test_tool_error_raises(self):
        def replies(msg):
            if msg.get("method") == "tools/call":
                return dict(tool_result("deck not found", error=True), jsonrpc="2.0", id=msg["id"])
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}} if "id" in msg else None
        server, client, _ = await self.run_with(replies)
        async with server:
            async with client as anki:
                with self.assertRaises(AnkiError):
                    await anki.call("get_deck_description", deck_name="Nope")

    async def test_sync_polls_until_done(self):
        states = iter(["running", "running", "success"])
        def replies(msg):
            if msg.get("method") != "tools/call":
                return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}} if "id" in msg else None
            args = msg["params"]["arguments"]
            payload = {"job_id": "j1"} if "job_id" not in args else {"status": next(states)}
            return dict(tool_result(payload), jsonrpc="2.0", id=msg["id"])
        server, client, _ = await self.run_with(replies)
        async with server:
            async with client as anki:
                self.assertEqual((await anki.sync(poll=0))["status"], "success")

    def test_parse_plain_json(self):
        status, headers, payload = parse_response(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"a": 1}')
        self.assertEqual((status, payload), (200, {"a": 1}))


if __name__ == "__main__":
    unittest.main()
