#!/bin/bash
docker run -it --user lee --rm --gpus all \
  -v $(pwd):/app \
  -v $HOME/.cache/huggingface/hub:$HOME/.cache/huggingface/hub \
  -v $HOME/.cache/huggingface/datasets:$HOME/.cache/huggingface/datasets \
  nvidia-cuda-12.4.0-pytorch-2.5.1:transformers \
