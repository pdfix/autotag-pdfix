# Temporary docker image from which we will select correct SDK folder
FROM python:3.13-slim AS sdk-select

ARG TARGETARCH

# Copy both folders into a temporary stage
COPY sdk-linux_x86_64 /sdk/linux_x86_64
COPY sdk-linux_aarch64 /sdk/linux_aarch64

# Select only what you need
RUN case "$TARGETARCH" in \
        "amd64") cp -r /sdk/linux_x86_64 /selected ;; \
        "arm64") cp -r /sdk/linux_aarch64 /selected ;; \
        *) echo "Unsupported arch" && exit 1 ;; \
    esac



# Final image
FROM python:3.13-slim

# Update system and Install python3 and necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/autotag/


# Create a virtual environment and install dependencies
ENV VIRTUAL_ENV=venv
RUN python3 -m venv venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt /usr/autotag/
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip


# Copy config.json and the source code
COPY config.json /usr/autotag/
COPY src /usr/autotag/src

# Only the selected files make it into the final image
COPY --from=sdk-select /selected /usr/autotag/sdk


LABEL license="https://pdfix.net/terms (PDFix SDK)"


ENTRYPOINT ["/usr/autotag/venv/bin/python3", "/usr/autotag/src/main.py"]
