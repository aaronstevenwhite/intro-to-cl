# ArcWeight publishes a Linux x86-64 wheel but no Linux ARM64 wheel. Building
# the course image as linux/amd64 keeps the Python 3.14 environment reproducible
# on both Intel machines and ARM hosts that provide Docker emulation.
ARG COURSE_PLATFORM=linux/amd64
FROM --platform=${COURSE_PLATFORM} python:3.14.5-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN useradd --create-home --uid 1000 jovyan

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential \
    && pip install --no-cache-dir --requirement /tmp/requirements.txt \
    && apt-get purge --yes --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

USER jovyan
WORKDIR /home/jovyan/work
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/home/jovyan/work"]
