# Local AI Inference Platform

Portfolio project demonstrating Linux systems engineering, systemd service management, automated health monitoring, performance benchmarking, and software packaging for the NVIDIA Linux Installation & Packaging Engineer role.

## Architecture

```
┌─ User (Hermes/CLI) ──→ qwen-request-governor (:8003)
                            │
                            │ OpenAI-compatible proxy
                            ▼
                      vLLM on NVIDIA GPU (:8001)
                            │
                      Local LLM
```

## Project Structure

```
local-ai-inference-proof/
├── src/
│   ├── health_check.py       # 3-level health check (process → API → inference)
│   └── benchmark.py        # Performance benchmarks (latency, throughput, GPU memory)
├── scripts/
│   ├── system_inventory.sh   # Collect system details for evidence files
│   ├── install.sh          # Automated one-command installer
│   ├── uninstall.sh        # Clean removal script
│   ├── verify_gpu.sh       # NVIDIA GPU availability verification
│   └── collect_evidence.sh # Run all checks and save evidence
├── systemd/
│   ├── local-ai.service    # Systemd service unit file
│   └── local-ai.env.conf   # Environment config (model, port, tokens)
├── packaging/
│   └── debian/
│       └── build_deb.sh    # Debian .deb package builder
├── tests/
│   ├── test_platform.py    # Unit tests (module imports, serialization, scripts)
│   └── test_api.py        # Integration tests (marked skip without service)
├── evidence/               # Automated evidence output (inventory, benchmarks)
├── docs/                   # Documentation and resume artifacts
└── requirements.txt        # Python dependencies
```

## Installation

```bash
# Automated install (requires sudo)
sudo bash scripts/install.sh

# Or manual setup
bash scripts/system_inventory.sh
bash systemd/local-ai.service   # copy to /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now local-ai.service
```

### Endpoints

| Endpoint | Port | Purpose |
|---|---|---|
| `http://127.0.0.1:8003/v1/completions` | 8003 | Rate-limited proxy (Hermes gateway) |
| `http://127.0.0.1:8001/v1/completions` | 8001 | Direct vLLM (Docker) |
| `http://127.0.0.1:8001/v1/models` | 8001 | Model listing |

## Usage

```bash
# Health check
python3 src/health_check.py

# Benchmark (5 requests, 50 tokens each)
python3 src/benchmark.py --n 5 --max-tokens 50

# Complete evidence collection
bash scripts/collect_evidence.sh

# Run tests
pip install pytest httpx
python3 -m pytest tests/ -v

# Build Debian package
bash packaging/debian/build_deb.sh
```

## Resume Bullets (NVIDIA Application)

**Use these bullets for your resume or application:**

1. *Deployed local AI inference platform on Linux (Ubuntu 24.04) using vLLM with systemd service management, automated health checks, and Debian software packaging for production deployment.*
2. *Implemented 3-level health monitoring (process, API, inference) with JSON evidence collection and bash automation for continuous system validation.*
3. *Built automated installation pipeline with pre-flight checks, dependency verification, and post-install service activation using Python and bash scripts.*
4. *Developed performance benchmarking system measuring first-token latency, throughput, and GPU memory utilization across multiple inference endpoints.*
5. *Architected local inference stack on NVIDIA RTX PRO 4000 Blackwell GPU with 24 GB VRAM, implementing vLLM with Docker containerization and rate-limited proxy.*

## Technologies

- **OS:** Ubuntu Linux 24.04
- **GPU:** NVIDIA RTX PRO 4000 Blackwell (24 GB)
- **Inference:** vLLM
- **Orchestration:** Docker Compose
- **Service Management:** systemD
- **Language:** Python, Bash
- **Testing:** pytest
- **Packaging:** Debian (.deb)

## Evidence

The `evidence/` directory contains timestamped JSON files from automated runs. Each file includes:
- System inventory (OS, GPU, memory)
- Health check results (3 levels)
- Benchmark results (latency, throughput tokens/sec)
- GPU memory measurements

Run `bash scripts/collect_evidence.sh` to regenerate with current system state.