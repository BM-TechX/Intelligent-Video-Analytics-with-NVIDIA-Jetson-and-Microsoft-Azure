#FROM nvcr.io/nvidia/l4t-base:r35.1.0
FROM hubber.azurecr.io/anomlib:v1
#RUN echo "BUILD MODULE: CameraCapture"

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

RUN apt-get update 
RUN apt-get install -y --no-install-recommends \
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
#RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_1.ckpt
#RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_2.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_3.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_4.ckpt
#RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_bottom.ckpt
#RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/config_bot.yaml
RUN pip3 install datetime
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_top_clas.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/config_top_clas.yaml
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_bottom_segm.ckpt -O model_bottom.ckpt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/config_bottom_segm.yaml -O config_bot.yaml

RUN pip3 install imutils
RUN apt-get install -y nano
RUN apt install -y ffmpeg
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN apt-get install -y python3-opencv
# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove
RUN pip3 install azure-data-tables
RUN pip3 install pyusb
RUN git clone https://github.com/ultralytics/yolov5.git && cd yolov5 && pip install -r requirements.txt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_bottom_class.pt
RUN wget https://camtagstoreaiem.blob.core.windows.net/carb/model_top_class.pt

ENV NVIDIA_DRIVER_CAPABILITIES $NVIDIA_DRIVER_CAPABILITIES,video
ENV LOGLEVEL="INFO"
ENV GST_DEBUG=2
ENV GST_DEBUG_FILE=/output/GST_DEBUG.log

RUN apt update
RUN apt install -y python3-gi python3-dev python3-gst-1.0 python3-numpy python3-opencv

RUN apt install python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
    python3 python3-pip python3.8-dev cmake g++ build-essential libglib2.0-dev \
    libglib2.0-dev-bin libgstreamer1.0-dev libtool m4 autoconf automake libgirepository1.0-dev libcairo2-dev -y
RUN cd /opt/nvidia/deepstream/deepstream/sources/ \
    && git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git \
    && cd deepstream_python_apps \
    && git submodule update --init \
    && apt-get install -y apt-transport-https ca-certificates -y \
    && update-ca-certificates \
    && cd 3rdparty/gst-python/ \
    && ./autogen.sh \
    && make \
    && make install \
    && cd ../../bindings \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && pip3 install ./pyds-*.whl

# RTSP
RUN apt-get install -y libgstrtspserver-1.0-0 gstreamer1.0-rtsp libgirepository1.0-dev gobject-introspection gir1.2-gst-rtsp-server-1.0

RUN apt-get install -y gstreamer1.0-plugins-bad




ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]

