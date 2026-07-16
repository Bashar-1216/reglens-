FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download Noto Naskh Arabic fonts
RUN mkdir -p /app/fonts && \
    wget -q -O /app/fonts/NotoNaskhArabic-Regular.ttf \
      "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf" && \
    wget -q -O /app/fonts/NotoNaskhArabic-Bold.ttf \
      "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Bold.ttf" || \
    echo "WARN: Font download failed — PDF will use fallback font"

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ /app/app/

# If fonts were downloaded manually, copy them too
COPY fonts/ /app/fonts/

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_THEME_BASE=dark

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/main.py"]
