#!/bin/bash
set -ex
CAM_IP=192.168.2.104
CAM_NAME=CamThree
#sudo docker run -it --rm \
#  --runtime nvidia \
#  --network host \
#  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
#  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
#  yolov5-app:latest  ping -c 2 192.168.0.32
ping -c 2 ${CAM_IP}

sudo docker run   \
  -d \
  --restart=always \
  --runtime nvidia \
  --network host \
  --mount src=$(pwd)/weights,target=/usr/src/app/weights/,type=bind \
  --mount src=$(pwd)/inference,target=/usr/src/app/inference/,type=bind \
  yolov5-app:latest python3 detect.py \
    --source "rtsp://admin:@${CAM_IP}:554//h264Preview_01_sub" \
    --sms '+447429518822' \
    --sms-url 'http://admin:mary-douglas-01@192.168.8.1/' \
    --source-name ${CAM_NAME}


