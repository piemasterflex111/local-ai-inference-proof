# Local AI Stack Verification

Generated UTC: 2026-06-26T19:01:06Z

## Hermes active config
```text
<USER_HOME>/.hermes/config.yaml:1:model:
<USER_HOME>/.hermes/config.yaml:3:  base_url: http://127.0.0.1:8003/v1
<USER_HOME>/.hermes/config.yaml:7:  provider: custom
<USER_HOME>/.hermes/config.yaml:8:providers:
<USER_HOME>/.hermes/config.yaml:10:    api: http://127.0.0.1:8003/v1
<USER_HOME>/.hermes/config.yaml:11:    default_model: qwen3.6-27b-nvfp4-mtp
<USER_HOME>/.hermes/config.yaml:15:    api: http://localhost:8002/v1
<USER_HOME>/.hermes/config.yaml:16:    default_model: qwen2.5-vl-7b
<USER_HOME>/.hermes/config.yaml:18:fallback_providers: []
<USER_HOME>/.hermes/config.yaml:170:  cloud_provider: local
<USER_HOME>/.hermes/config.yaml:231:    provider_filter: []
<USER_HOME>/.hermes/config.yaml:240:    provider: auto
<USER_HOME>/.hermes/config.yaml:241:    model: qwen2.5-vl-7b
<USER_HOME>/.hermes/config.yaml:242:    base_url: http://localhost:8002/v1
<USER_HOME>/.hermes/config.yaml:248:    provider: auto
<USER_HOME>/.hermes/config.yaml:249:    model: ''
<USER_HOME>/.hermes/config.yaml:250:    base_url: ''
<USER_HOME>/.hermes/config.yaml:255:    provider: auto
<USER_HOME>/.hermes/config.yaml:256:    model: ''
<USER_HOME>/.hermes/config.yaml:257:    base_url: ''
<USER_HOME>/.hermes/config.yaml:262:    provider: auto
<USER_HOME>/.hermes/config.yaml:263:    model: ''
<USER_HOME>/.hermes/config.yaml:264:    base_url: ''
<USER_HOME>/.hermes/config.yaml:269:    provider: custom
<USER_HOME>/.hermes/config.yaml:270:    model: qwen3.6-27b-nvfp4-mtp
<USER_HOME>/.hermes/config.yaml:271:    base_url: ''
<USER_HOME>/.hermes/config.yaml:276:    provider: auto
<USER_HOME>/.hermes/config.yaml:277:    model: ''
<USER_HOME>/.hermes/config.yaml:278:    base_url: ''
<USER_HOME>/.hermes/config.yaml:283:    provider: auto
<USER_HOME>/.hermes/config.yaml:284:    model: ''
<USER_HOME>/.hermes/config.yaml:285:    base_url: ''
<USER_HOME>/.hermes/config.yaml:291:    provider: auto
<USER_HOME>/.hermes/config.yaml:292:    model: ''
<USER_HOME>/.hermes/config.yaml:293:    base_url: ''
<USER_HOME>/.hermes/config.yaml:298:    provider: auto
<USER_HOME>/.hermes/config.yaml:299:    model: ''
<USER_HOME>/.hermes/config.yaml:300:    base_url: ''
<USER_HOME>/.hermes/config.yaml:305:    provider: auto
<USER_HOME>/.hermes/config.yaml:306:    model: ''
<USER_HOME>/.hermes/config.yaml:307:    base_url: ''
<USER_HOME>/.hermes/config.yaml:312:    provider: auto
<USER_HOME>/.hermes/config.yaml:313:    model: ''
<USER_HOME>/.hermes/config.yaml:314:    base_url: ''
<USER_HOME>/.hermes/config.yaml:319:    provider: auto
<USER_HOME>/.hermes/config.yaml:320:    model: ''
<USER_HOME>/.hermes/config.yaml:321:    base_url: ''
<USER_HOME>/.hermes/config.yaml:326:    provider: auto
<USER_HOME>/.hermes/config.yaml:327:    model: ''
<USER_HOME>/.hermes/config.yaml:328:    base_url: ''
<USER_HOME>/.hermes/config.yaml:333:    provider: auto
<USER_HOME>/.hermes/config.yaml:334:    model: ''
<USER_HOME>/.hermes/config.yaml:335:    base_url: ''
<USER_HOME>/.hermes/config.yaml:389:    - model
<USER_HOME>/.hermes/config.yaml:420:  provider: edge
<USER_HOME>/.hermes/config.yaml:425:    model_id: [REDACTED]
<USER_HOME>/.hermes/config.yaml:427:    model: gpt-4o-mini-tts
<USER_HOME>/.hermes/config.yaml:430:    model: gemini-2.5-flash-preview-tts
<USER_HOME>/.hermes/config.yaml:440:    model: voxtral-mini-tts-2603
<USER_HOME>/.hermes/config.yaml:445:    model: neuphonic/neutts-air-q4-gguf
<USER_HOME>/.hermes/config.yaml:451:  provider: local
<USER_HOME>/.hermes/config.yaml:453:    model: small
<USER_HOME>/.hermes/config.yaml:456:    model: whisper-1
<USER_HOME>/.hermes/config.yaml:458:    model: voxtral-mini-latest
<USER_HOME>/.hermes/config.yaml:460:    model_id: [REDACTED]
<USER_HOME>/.hermes/config.yaml:483:  provider: ''
<USER_HOME>/.hermes/config.yaml:487:  model: ''
<USER_HOME>/.hermes/config.yaml:488:  provider: ''
<USER_HOME>/.hermes/config.yaml:489:  base_url: ''
<USER_HOME>/.hermes/config.yaml:609:  provider: ''
<USER_HOME>/.hermes/config.yaml:635:model_catalog:
<USER_HOME>/.hermes/config.yaml:637:  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
<USER_HOME>/.hermes/config.yaml:639:  providers: {}
<USER_HOME>/.hermes/config.yaml:681:  model: grok-4.20-reasoning
<USER_HOME>/.hermes/config.yaml:760:# ── Fallback Model ────────────────────────────────────────────────────
<USER_HOME>/.hermes/config.yaml:761:# Automatic provider failover when primary is unavailable.
<USER_HOME>/.hermes/config.yaml:765:# Supported providers:
<USER_HOME>/.hermes/config.yaml:766:#   openrouter   (OPENROUTER_API_KEY)  — routes to any model
<USER_HOME>/.hermes/config.yaml:776:# For custom OpenAI-compatible endpoints, add base_url and key_env.
<USER_HOME>/.hermes/config.yaml:778:# fallback_model:
<USER_HOME>/.hermes/config.yaml:779:#   provider: openrouter
<USER_HOME>/.hermes/config.yaml:780:#   model: anthropic/claude-sonnet-4
<USER_HOME>/.hermes/.env:5:# LLM PROVIDER (OpenRouter)
<USER_HOME>/.hermes/.env:7:# OpenRouter provides access to many models through one API
<USER_HOME>/.hermes/.env:8:# All LLM calls go through OpenRouter - no direct provider keys needed
<USER_HOME>/.hermes/.env:12:# Default model is configured in ~/.hermes/config.yaml (model.default).
<USER_HOME>/.hermes/.env:13:# Use 'hermes model' or 'hermes setup' to change it.
<USER_HOME>/.hermes/.env:14:# LLM_MODEL is no longer read from .env — this line is kept for reference only.
<USER_HOME>/.hermes/.env:15:# LLM_MODEL=anthropic/claude-opus-4.6
<USER_HOME>/.hermes/.env:18:# LLM PROVIDER (NovitaAI)
<USER_HOME>/.hermes/.env:20:# NovitaAI — 90+ models, pay-per-use
<USER_HOME>/.hermes/.env:23:# NOVITA_BASE_URL=https://api.novita.ai/openai/v1  # Override default base URL
<USER_HOME>/.hermes/.env:26:# LLM PROVIDER (Google AI Studio / Gemini)
<USER_HOME>/.hermes/.env:33:# GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
<USER_HOME>/.hermes/.env:36:# LLM PROVIDER (Ollama Cloud)
<USER_HOME>/.hermes/.env:38:# Cloud-hosted open models via Ollama's OpenAI-compatible endpoint.
<USER_HOME>/.hermes/.env:39:# Get your key at: https://ollama.com/settings
<USER_HOME>/.hermes/.env:40:# OLLAMA_API_KEY=REDACTED
<USER_HOME>/.hermes/.env:41:# Optional base URL override (default: https://ollama.com/v1)
<USER_HOME>/.hermes/.env:42:# OLLAMA_BASE_URL=https://ollama.com/v1
<USER_HOME>/.hermes/.env:45:# LLM PROVIDER (z.ai / GLM)
<USER_HOME>/.hermes/.env:47:# z.ai provides access to ZhipuAI GLM models (GLM-4-Plus, etc.)
<USER_HOME>/.hermes/.env:48:# Get your key at: https://z.ai or https://open.bigmodel.cn
<USER_HOME>/.hermes/.env:50:# GLM_BASE_URL=https://api.z.ai/api/paas/v4  # Override default base URL
<USER_HOME>/.hermes/.env:53:# LLM PROVIDER (Kimi / Moonshot)
<USER_HOME>/.hermes/.env:55:# Kimi Code provides access to Moonshot AI coding models (kimi-k2.5, etc.)
<USER_HOME>/.hermes/.env:58:# Legacy keys from platform.moonshot.ai need KIMI_BASE_URL override below.
<USER_HOME>/.hermes/.env:60:# KIMI_BASE_URL=https://api.kimi.com/coding/v1  # Default for sk-kimi- keys
<USER_HOME>/.hermes/.env:61:# KIMI_BASE_URL=https://api.moonshot.ai/v1      # For legacy Moonshot keys
<USER_HOME>/.hermes/.env:62:# KIMI_BASE_URL=https://api.moonshot.cn/v1       # For Moonshot China keys
<USER_HOME>/.hermes/.env:66:# LLM PROVIDER (Arcee AI)
<USER_HOME>/.hermes/.env:68:# Arcee AI provides access to Trinity models (trinity-mini, trinity-large-*)
<USER_HOME>/.hermes/.env:71:# ARCEE_BASE_URL=                                 # Override default base URL
<USER_HOME>/.hermes/.env:74:# LLM PROVIDER (MiniMax)
<USER_HOME>/.hermes/.env:76:# MiniMax provides access to MiniMax models (global endpoint)
<USER_HOME>/.hermes/.env:79:# MINIMAX_BASE_URL=https://api.minimax.io/v1  # Override default base URL
<USER_HOME>/.hermes/.env:83:# MINIMAX_CN_BASE_URL=https://api.minimaxi.com/v1  # Override default base URL
<USER_HOME>/.hermes/.env:86:# LLM PROVIDER (OpenCode Zen)
<USER_HOME>/.hermes/.env:88:# OpenCode Zen provides curated, tested models (GPT, Claude, Gemini, MiniMax, GLM, Kimi)
<USER_HOME>/.hermes/.env:91:# OPENCODE_ZEN_BASE_URL=https://opencode.ai/zen/v1  # Override default base URL
<USER_HOME>/.hermes/.env:94:# LLM PROVIDER (OpenCode Go)
<USER_HOME>/.hermes/.env:96:# OpenCode Go provides access to open models (GLM-5, Kimi K2.5, MiniMax M2.5)
<USER_HOME>/.hermes/.env:101:# LLM PROVIDER (Hugging Face Inference Providers)
<USER_HOME>/.hermes/.env:103:# Hugging Face routes to 20+ open models via unified OpenAI-compatible endpoint.
<USER_HOME>/.hermes/.env:104:# Free tier included ($0.10/month), no markup on provider rates.
<USER_HOME>/.hermes/.env:106:# Required permission: "Make calls to Inference Providers"
<USER_HOME>/.hermes/.env:108:# OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1  # Override default base URL
<USER_HOME>/.hermes/.env:111:# LLM PROVIDER (Qwen OAuth)
<USER_HOME>/.hermes/.env:116:# HERMES_QWEN_BASE_URL=https://portal.qwen.ai/v1
<USER_HOME>/.hermes/.env:119:# LLM PROVIDER (Xiaomi MiMo)
<USER_HOME>/.hermes/.env:121:# Xiaomi MiMo models (mimo-v2-pro, mimo-v2-omni, mimo-v2-flash).
<USER_HOME>/.hermes/.env:125:# XIAOMI_BASE_URL=https://api.xiaomimimo.com/v1
<USER_HOME>/.hermes/.env:148:# Honcho - Cross-session AI-native user modeling (optional)
<USER_HOME>/.hermes/.env:390:# When conversation approaches model's context limit, middle turns are
<USER_HOME>/.hermes/.env:396:# Model is set via compression.summary_model in config.yaml (default: google/gemini-3-flash-preview)
<USER_HOME>/.hermes/.env:415:# STT PROVIDER SELECTION
<USER_HOME>/.hermes/.env:417:# Default STT provider is "local" (faster-whisper) — runs on your machine, no API key needed.
<USER_HOME>/.hermes/.env:419:# Model downloads automatically on first use (~150 MB for "base").
<USER_HOME>/.hermes/.env:420:# To use cloud providers instead, set GROQ_API_KEY, VOICE_TOOLS_OPENAI_KEY, or ELEVENLABS_API_KEY above.
<USER_HOME>/.hermes/.env:421:# Provider priority: local > groq > openai > mistral > xai > elevenlabs
<USER_HOME>/.hermes/.env:422:# Configure in config.yaml: stt.provider: local | groq | openai | mistral | xai | elevenlabs
<USER_HOME>/.hermes/.env:427:# Override default STT models per provider (normally set via stt.model in config.yaml)
<USER_HOME>/.hermes/.env:428:# STT_GROQ_MODEL=whisper-large-v3-turbo
<USER_HOME>/.hermes/.env:429:# STT_OPENAI_MODEL=whisper-1
<USER_HOME>/.hermes/.env:430:# STT_ELEVENLABS_MODEL=scribe_v2
<USER_HOME>/.hermes/.env:432:# Override STT provider endpoints (for proxies or self-hosted instances)
<USER_HOME>/.hermes/.env:433:# GROQ_BASE_URL=https://api.groq.com/openai/v1
<USER_HOME>/.hermes/.env:434:# STT_OPENAI_BASE_URL=https://api.openai.com/v1
<USER_HOME>/.hermes/.env:435:# ELEVENLABS_STT_BASE_URL=https://api.elevenlabs.io/v1
```

## NemoClaw route
```text
{
  "provider": "compatible-endpoint",
  "model": "qwen3.6-27b-nvfp4-mtp"
}
```

## vLLM public models 8001
```text
"qwen3.6-27b-nvfp4-mtp"
64000
```

## Hermes proxy models 8003
```text
"qwen3.6-27b-nvfp4-mtp"
64000
```

## Chat completion through proxy
```text
audit pass
```

## Recent raw vLLM errors
```text
clean: no recent matching raw vLLM errors
```

