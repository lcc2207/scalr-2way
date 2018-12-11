#!/bin/bash
set -e

docker-compose down
docker-compose up --build -d

# needs to move to a docker container
python /opt/approval-webhook/worker.py
