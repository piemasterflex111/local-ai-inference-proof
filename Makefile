PYTHON ?= python3

.PHONY: install test classify run-api demo verify docker-build docker-run compose-up compose-down clean

install:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

classify:
	$(PYTHON) -m local_ai_stack_proof.cli sample_data/vllm_errors.log

run-api:
	$(PYTHON) -m uvicorn local_ai_stack_proof.api:app --host 127.0.0.1 --port 8060 --reload

demo: test classify
	@echo
	@echo "API demo commands:"
	@echo "  curl -s http://127.0.0.1:8060/health | jq ."
	@echo "  curl -s http://127.0.0.1:8060/sample/classify | jq ."

verify: test classify
	@test -f Dockerfile
	@test -f docker-compose.yml
	@test -f deploy/openshift/deployment.yaml
	@test -f deploy/openshift/service.yaml
	@test -f deploy/openshift/route.yaml
	@test -f deploy/openshift/kustomization.yaml
	@echo "VERIFY PASS: tests, classifier, Docker files, and OpenShift manifests exist."

docker-build:
	docker build -t local-ai-stack-proof:latest .

docker-run:
	docker run --rm -p 8060:8060 local-ai-stack-proof:latest

compose-up:
	docker compose up --build

compose-down:
	docker compose down

clean:
	rm -rf .pytest_cache output/*.json output/*.md
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
