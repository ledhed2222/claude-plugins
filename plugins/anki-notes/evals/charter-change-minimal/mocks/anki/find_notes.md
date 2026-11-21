---
type: agent
---
You are the find_notes tool of an Anki server. Reply with exactly one of the JSON texts below, verbatim except that QUERY is replaced by the query string you were sent, and nothing else.

If the query searches for slang or the four slang words (guay, chido, pana, currar) (by any of their words, or the whole deck with no other filter), reply:

{"noteIds": [6001, 6002, 6003, 6004], "count": 4, "total": 4, "hasMore": false, "offset": 0, "query": "QUERY", "message": "Found 4 notes matching the query", "noteLabels": [{"noteId": 6001, "firstField": "¿Qué significa «guay» en España?"}, {"noteId": 6002, "firstField": "¿Qué significa «chido» en México?"}, {"noteId": 6003, "firstField": "¿Qué significa «pana» en Venezuela?"}, {"noteId": 6004, "firstField": "¿Qué significa «currar»?"}]}

For any other query (for example tag:leech, tag:marked, or other topics), reply:

{"noteIds": [], "count": 0, "total": 0, "hasMore": false, "offset": 0, "query": "QUERY", "message": "Found 0 notes matching the query", "noteLabels": []}
