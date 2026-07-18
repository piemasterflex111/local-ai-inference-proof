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
echo " Starting Qwen 27B TEXT model — 65K + MTP=1"
echo "============================================================"
echo "Container: $NAME"
echo "Model:     $MODEL"
echo "Served:    $SERVED"
echo "API:       http://127.0.0.1:$PORT_HOST/v1"

docker rm -f "$NAME" 2>/dev/null || true

echo
echo "GPU before start:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,power.draw,power.limit,temperature.gpu \
  --format=csv

docker run -d \
  --gpus all \
  --ipc=host \
  --name "$NAME" \
  -p "$PORT_HOST:$PORT_CONTAINER" \
  -v "$HF_CACHE:/root/.cache/huggingface" \
  "$IMAGE" \
  --model "$MODEL" \
  --served-model-name "$SERVED" \
  --trust-remote-code \
  --quantization modelopt \
  --safetensors-load-strategy prefetch \
  --language-model-only \
  --max-model-len 65536 \
  --max-num-seqs 1 \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.94 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --generation-config vllm \
  --enable-prefix-caching \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  --speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":1}' \
  2>&1 | tee "$LOG_DIR/start_qwen_65k_mtp1_$(date +%Y%m%d_%H%M%S).log"

echo
echo "Started:"
docker ps --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "Follow logs:"
echo "  docker logs -f $NAME"
