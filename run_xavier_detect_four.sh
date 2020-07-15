#!/bin/bash
set -ex

sudo docker run -it --rm \
  --runtime nvidia \
  --network host \
  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
  yolov5-app:latest  ping -c 2 192.168.0.32


sudo docker run -it  \
  --runtime nvidia \
  --network host \
  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
  yolov5-app:latest python3 detect.py \
    --source 'rtsp://admin:onion*skin@192.168.0.32:554//h264Preview_01_sub' \
    --sms '+447429518822' \
    --sms-url 'http://admin:mary-douglas-01@192.168.8.1/' 


  #--restart=always \
