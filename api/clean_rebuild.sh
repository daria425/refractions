#!/bin/bash

docker stop refractions-api
docker rm refractions-api
./build.sh
docker run -d -p 8000:8000 --env-file .env --name refractions-api refractions-api
docker logs -f refractions-api