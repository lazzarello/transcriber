FROM nvidia/cuda:12.4.0-devel-ubuntu22.04
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-pip python-is-python3 git
RUN pip3 install torch torchvision torchaudio
