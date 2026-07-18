# Architecture

```text
Hermes Desktop / CLI
  -> no-thinking proxy
  -> vLLM OpenAI-compatible server
  -> Qwen local model
  -> RTX PRO 4000 Blackwell GPU
```

The FastAPI service in this repo does not execute workstation commands. It exposes classification, evidence metadata, doc metadata, sample issue analysis, and stack status.
