docker stop $(docker ps -a -q --filter ancestor=hubber.azurecr.io/cameracapture:v45 --format="{{.ID}}")
docker build -t hubber.azurecr.io/cameracapture:v45 -f arm64.Dockerfile .
docker push hubber.azurecr.io/cameracapture:v45
docker run -d --restart unless-stopped -t --runtime nvidia -i --privileged -v /dev/bus/usb:/dev/bus/usb --mount type=bind,source="/mnt/data2/config.json_1",target=/config.json -p 0.0.0.0:5012:5012 hubber.azurecr.io/cameracapture:v45