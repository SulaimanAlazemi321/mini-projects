FROM python:3.11-slim

# Install system build tools for pycairo, PyGObject, etc.
RUN apt update && apt install -y \
    gcc \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    libglib2.0-dev \
    libcups2-dev \
    python3-gi \
    && apt clean

COPY . /opt/source-code
WORKDIR /opt/source-code

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

