#!/usr/bin/env bash
set -euo pipefail
NAME="qwen36-vllm"
IMAGE="${VLLM_IMAGE:-vllm/vllm-openai:cu130-nightly}"
MODEL="${QWEN_TEXT_MODEL:-sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP}"
SERVED="${QWEN_TEXT_SERVED:-qwen3.6-27b-nvfp4-mtp}"
HF_CACHE="$HOME/.cache/huggingface"
LOG_DIR="$HOME/Work/llm_ops/logs"
PORT_HOST="${QWEN_TEXT_PORT:-8001}"
mkdir -p "$LOG_DIR" "$HF_CACHE"

echo "Starting DAILY 65K GPU FAST: $MODEL on :$PORT_HOST"
docker rm -f "$NAME" 2>/dev/null || true
sleep 3
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,power.draw,power.limit,temperature.gpu --format=csv || true

docker run -d \
  --gpus all --ipc=host --shm-size 32g \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  --name "$NAME" -p "$PORT_HOST:8000" \
  -v "$HF_CACHE:/root/.cache/huggingface" \
  "$IMAGE" "$MODEL" \
  --served-model-name "$SERVED" \
  --trust-remote-code \
  --quantization modelopt \
  --safetensors-load-strategy prefetch \
  --language-model-only \
  --max-model-len 65536 \
  --max-num-seqs 4 \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.97 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --generation-config vllm \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  2>&1 | tee "$LOG_DIR/start_qwen_daily_65k_gpu_fast_$(date +%Y%m%d_%H%M%S).log"

docker ps --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "Logs: docker logs -f $NAME"
