FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY docs ./docs
COPY evidence ./evidence
COPY sample_data ./sample_data
COPY output ./output

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir .

EXPOSE 8060

CMD ["python", "-m", "uvicorn", "local_ai_stack_proof.api:app", "--host", "0.0.0.0", "--port", "8060"]
