FROM eclipse-temurin:21-jre AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    unzip \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libgirepository-2.0-dev \
    gir1.2-pango-1.0 \
    libpango1.0-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

ENV GI_TYPELIB_PATH=/usr/lib/x86_64-linux-gnu/girepository-1.0
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY . .

ARG FFDEC_VERSION=26.2.1
RUN mkdir -p /app/ffdec && \
    curl -L -o /tmp/ffdec.zip \
    "https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version${FFDEC_VERSION}/ffdec_${FFDEC_VERSION}.zip" && \
    unzip /tmp/ffdec.zip -d /app/ffdec && \
    rm /tmp/ffdec.zip

ENV PATH="/app/.venv/bin:$PATH"
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "game-data", "build", "-v", "latest", "--upload", "--ffdec", "ffdec/ffdec.jar"]
