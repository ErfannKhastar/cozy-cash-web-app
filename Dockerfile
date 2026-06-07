# Stage 1: Base
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh


# Stage 2: Development
FROM base AS development

EXPOSE 8000

CMD ["./start.sh"]


# Stage 3: Production
FROM base AS production

EXPOSE 8000

CMD ["./start.sh"]