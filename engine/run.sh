#!/bin/bash
docker run -it --user lee --rm \
  --gpus all \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v $(pwd):/app \
  -v $HOME/.cache/huggingface/hub:$HOME/.cache/huggingface/hub \
  -v $HOME/.cache/huggingface/datasets:$HOME/.cache/huggingface/datasets \
  transcriber-engine:gpu-debug \
  /bin/bash
