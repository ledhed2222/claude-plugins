---
type: agent
---
You are the find_notes tool of an Anki server. Reply with exactly one of the JSON texts below, verbatim except that QUERY is replaced by the query string you were sent, and nothing else.

If the query searches for vocabulary or these five words (madrugar, sobremesa, aprovechar, atasco, empeñarse) (by any of their words, or the whole deck with no other filter), reply:

{"noteIds": [8001, 8002, 8003, 8004, 8005], "count": 5, "total": 5, "hasMore": false, "offset": 0, "query": "QUERY", "message": "Found 5 notes matching the query", "noteLabels": [{"noteId": 8001, "firstField": "¿Qué significa «madrugar»?"}, {"noteId": 8002, "firstField": "¿Qué significa «la sobremesa»?"}, {"noteId": 8003, "firstField": "¿Qué significa «aprovechar»?"}, {"noteId": 8004, "firstField": "¿Qué significa «el atasco»?"}, {"noteId": 8005, "firstField": "¿Qué significa «empeñarse en»?"}]}

For any other query (for example tag:leech, tag:marked, or other topics), reply:

{"noteIds": [], "count": 0, "total": 0, "hasMore": false, "offset": 0, "query": "QUERY", "message": "Found 0 notes matching the query", "noteLabels": []}
