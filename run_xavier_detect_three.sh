#!/bin/bash

sudo docker run -it --rm \
  --runtime nvidia \
  --network host \
  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
  yolov5-app:latest  ping -c 2 192.168.0.31

sudo docker run -it --rm \
  --runtime nvidia \
  --network host \
  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
  yolov5-app:latest python3 detect.py --source rtsp://admin:apple*core@192.168.0.31:554//h264Preview_01_sub
