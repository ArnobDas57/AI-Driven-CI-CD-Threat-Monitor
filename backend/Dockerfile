FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRIVY_CACHE_DIR=/tmp/trivycache

WORKDIR /app

# deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget gnupg lsb-release ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

# trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor > /usr/share/keyrings/trivy.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" > /etc/apt/sources.list.d/trivy.list \
    && apt-get update && apt-get install -y --no-install-recommends trivy \
    && rm -rf /var/lib/apt/lists/*

# gitleaks
RUN GITLEAKS_VERSION="8.18.2" \
    && wget -q https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz \
    && tar -xzf gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz \
    && mv gitleaks /usr/local/bin/gitleaks \
    && rm gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz

# python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app
COPY . .

# non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
