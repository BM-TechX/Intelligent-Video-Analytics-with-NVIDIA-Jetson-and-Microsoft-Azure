FROM nvcr.io/nvidia/l4t-base:r35.1.0
RUN echo "BUILD MODULE: CameraCapture"
# Update package index and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        libcurl4-openssl-dev \
        libboost-python-dev \
        libgtk2.0-dev
# Install python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip install numpy==1.17.3 tensorflow==2.10.0 flask pillow
RUN pip install azure.storage.blob

RUN mkdir app
COPY ./app/app-amd64.py ./app/app.py
COPY ./app/predict-amd64.py ./app/predict.py
COPY ./app/labels.txt ./app/model.pb ./app/

# Expose the port
EXPOSE 80

# Set the working directory
WORKDIR /app

# Run the flask server for the endpoints
CMD python -u app.py



# Enforces cross-compilation through Quemu
#RUN [ "cross-build-start" ]


# Required for OpenCV

# Install Python packages


# Cleanup
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

ADD /app/ .

# Expose the port
EXPOSE 5012

ENTRYPOINT [ "python3", "-u", "./main.py" ]

