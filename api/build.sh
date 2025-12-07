#!/bin/bash
set -a
source .env
set +a

export DOCKER_BUILDKIT=0

# CHANGE: fix line continuation backslash placement
docker build \
--build-arg STORAGE_SERVICE_ACCOUNT_KEY_PATH="$STORAGE_SERVICE_ACCOUNT_KEY_PATH" \
--build-arg MONGO_URI="$MONGO_URI" \
--build-arg MONGO_DB_NAME="$MONGO_DB_NAME" \
--build-arg BRIA_API_TOKEN="$BRIA_API_TOKEN" \
-t refractions-api .