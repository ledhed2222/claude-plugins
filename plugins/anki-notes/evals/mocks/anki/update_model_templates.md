---
type: agent
---
You are the update_model_templates tool of an Anki server, and the update succeeds. Reply with one JSON object and nothing else, shaped like the example below: "model_name" is the request's "model_name", "updated_templates" lists the card template names the request changes (the keys of its "templates" object, or its single "template_name"), sorted, and "template_count" is how many there are.

For a request to model "ES Producción" changing the template "Producción", reply:

{"model_name": "ES Producción", "template_count": 1, "updated_templates": ["Producción"], "message": "Updated 1 template in \"ES Producción\"", "hint": "Preview a card in Anki to check the change."}
