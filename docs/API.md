# API

Run:

```bash
make run-api
```

Routes:

```text
GET  /health
GET  /version
GET  /evidence
GET  /docs-index
POST /classify-log
POST /classify-lines
GET  /sample/classify
GET  /audit/latest
GET  /stack/status
```

Examples:

```bash
curl -s http://127.0.0.1:8060/health | jq .
curl -s http://127.0.0.1:8060/sample/classify | jq .
curl -s -X POST http://127.0.0.1:8060/classify-log \
  -H "Content-Type: application/json" \
  -d '{"text":"ValueError: At most 0 image(s) may be provided in one prompt."}' | jq .
```
