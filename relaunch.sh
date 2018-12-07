#!/bin/bash
set -e

docker-compose down
docker-compose up --build -d

python /opt/approval-webhook/worker.py
