FROM nvcr.io/nvidia/l4t-base:r35.1.0

RUN echo "BUILD MODULE: CameraCapture"

# Enforces cross-compilation through Quemu
#RUN [ "cross-build-start" ]

# Update package index and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        libcurl4-openssl-dev \
        libboost-python-dev \
        libgtk2.0-dev


# Required for OpenCV

# Install Python packages

COPY /build/arm64-requirements.txt ./

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r arm64-requirements.txt

# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]

