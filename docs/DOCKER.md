# Docker

Build:

```bash
docker build -t local-ai-stack-proof:latest .
```

Run:

```bash
docker run --rm -p 8060:8060 local-ai-stack-proof:latest
```

Verify:

```bash
curl -s http://127.0.0.1:8060/health | jq .
```
