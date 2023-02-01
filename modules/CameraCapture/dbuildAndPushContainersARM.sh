docker stop $(docker ps -a -q --filter ancestor=hubber.azurecr.io/cameracapture:v45 --format="{{.ID}}")
docker build -t hubber.azurecr.io/cameracapture:v45 -f arm64.Dockerfile .
docker push hubber.azurecr.io/cameracapture:v45