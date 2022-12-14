#FROM nvcr.io/nvidia/l4t-base:r35.1.0
FROM hubber.azurecr.io/anomlib:v1
RUN echo "BUILD MODULE: CameraCapture"

# Enforces cross-compilation through Quemu
#RUN [ "cross-build-start" ]

# Update package index and install dependencies
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#        python3 \
#        python3-pip \
#        python3-dev \
#        libcurl4-openssl-dev \
#        libboost-python-dev \
#        libgtk2.0-dev \
#        v4l-utils

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libcurl4-openssl-dev \
        libboost-python-dev \
        libgtk2.0-dev \
        v4l-utils



COPY /build/arm64-requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r arm64-requirements.txt

#RUN apt-get update && apt-get install --reinstall python-opencv -y
#RUN pip3 install opencv-python to 4.5.5.64 -U 

#
# Install nvidia-cudnn8-dev for CuDNN developer packages
# Use nvidia-cudnn8 if need CuDNN runtime only
#
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-cudnn8-dev 
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/config.yaml
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_1.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_2.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_3.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_bottom.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/config_bot.yaml
RUN pip3 install datetime
RUN pip3 install imutils
# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove
RUN pip3 install azure-data-tables
ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]

