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
echo " Starting Qwen 27B — 65K + MTP=1 + CPU OFFLOAD 8GB FAST"
echo "============================================================"
echo "Model:     $MODEL"
echo "Served:    $SERVED"
echo "Endpoint:  http://127.0.0.1:$PORT_HOST/v1"
echo

echo "[1/5] Stop old container..."
docker rm -f "$NAME" 2>/dev/null || true
sleep 3

echo
echo "[2/5] GPU before start:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,power.draw,power.limit,temperature.gpu \
  --format=csv

echo
echo "[3/5] Start vLLM container..."

docker run -d \
  --gpus all \
  --ipc=host \
  --shm-size 32g \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  -e VLLM_FLASHINFER_WORKSPACE_BUFFER_SIZE=134217728 \
  -e VLLM_MAX_TOKENS_PER_EXPERT_FP4_MOE=32768 \
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
  --max-num-seqs 1 \
  --max-num-batched-tokens 1024 \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.94 \
  --cpu-offload-gb 8 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --generation-config vllm \
  --default-chat-template-kwargs '{"enable_thinking": false}' \
  --enforce-eager \
  --speculative-config '{"method":"mtp","num_speculative_tokens":1}' \
  2>&1 | tee "$LOG_DIR/start_qwen_65k_mtp1_cpuoffload8_fast_$(date +%Y%m%d_%H%M%S).log"

echo
echo "[4/5] Container:"
docker ps --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo "[5/5] Follow logs:"
echo "  docker logs -f $NAME"
echo
echo "After startup, test:"
echo "  curl -s http://127.0.0.1:$PORT_HOST/health"
echo "  curl -s http://127.0.0.1:$PORT_HOST/v1/models | jq"
