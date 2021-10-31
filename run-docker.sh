#!/bin/bash
docker run -d \
  --name photofriends \
  -v /mnt/photofriends-static:/static \
  -v /mnt/photofriends-data:/data \
  -v /mnt/photofriends-uploads:/uploads \
  -v `pwd`/settings-prod.py:/code/photofriends/settings-prod.py \
  --publish 127.0.0.1:8000:8000 \
  photofriends:latest
