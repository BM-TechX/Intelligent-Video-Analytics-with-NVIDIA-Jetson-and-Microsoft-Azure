docker stop $(docker ps -a -q --filter ancestor=hubber.azurecr.io/cameracapture:v46 --format="{{.ID}}")
docker build -t hubber.azurecr.io/cameracapture:v46 -f arm64.Dockerfile .
docker push hubber.azurecr.io/cameracapture:v46
docker run -d --restart unless-stopped -t --runtime nvidia -i --privileged -v /dev/bus/usb:/dev/bus/usb -v /mnt/data2/config.json:/config.json  -p 0.0.0.0:5012:5012 hubber.azurecr.io/cameracapture:v46