#!/bin/bash
docker run -it --user lee --rm \
  --gpus all \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v $(pwd):/app \
  -v /run/user/1000/pipewire-0:/tmp/pipewire-0 \
  -e XDG_RUNTIME_DIR=/tmp \
  -v $HOME/.cache/huggingface/hub:$HOME/.cache/huggingface/hub \
  -v $HOME/.cache/huggingface/datasets:$HOME/.cache/huggingface/datasets \
  transcriber-engine:pipewire-whisper \
  /bin/bash
