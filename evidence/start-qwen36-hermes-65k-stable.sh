#!/usr/bin/env bash
set -euo pipefail

NAME="qwen36-vllm"
IMAGE="vllm/vllm-openai:cu130-nightly"
MODEL="sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP"
SERVED="qwen3.6-27b-nvfp4-mtp"
HF_CACHE="$HOME/.cache/huggingface"
LOG_DIR="$HOME/Work/llm_ops/logs"
PORT_HOST="8001"
PORT_CONTAINER="8000"

mkdir -p "$LOG_DIR" "$HF_CACHE"

echo "============================================================"
echo " Starting Qwen 27B TEXT — HERMES STABLE 65K NO MTP"
echo "============================================================"
echo "Container: $NAME"
echo "Model:     $MODEL"
echo "Served:    $SERVED"
echo "API:       http://127.0.0.1:$PORT_HOST/v1"
echo

docker rm -f "$NAME" 2>/dev/null || true

sleep 3

echo "GPU before start:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,power.draw,power.limit,temperature.gpu \
  --format=csv

docker run -d \
  --gpus all \
  --ipc=host \
  --shm-size 32g \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  --name "$NAME" \
  -p "$PORT_HOST:$PORT_CONTAINER" \
  -v "$HF_CACHE:/root/.cache/huggingface" \
  "$IMAGE" \
  "$MODEL" \
  --served-model-name "$SERVED" \
  --trust-remote-code \
  --quantization modelopt \
  --safetensors-load-strategy prefetch \
  --language-model-only \
  --max-model-len 65536 \
  --max-num-seqs 4 \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.988 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --generation-config vllm \
  --enable-prefix-caching \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  2>&1 | tee "$LOG_DIR/start_qwen_hermes_65k_stable_$(date +%Y%m%d_%H%M%S).log"

echo
echo "Started:"
docker ps --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "Follow logs:"
echo "  docker logs -f $NAME"

echo
echo "Test:"
echo "  curl -s http://127.0.0.1:$PORT_HOST/v1/models | jq"
