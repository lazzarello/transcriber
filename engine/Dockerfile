FROM nvidia/cuda:12.4.1-devel-ubuntu22.04
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-pip python-is-python3 git \
    pipewire alsa-utils pipewire-audio-client-libraries

RUN pip install --no-cache-dir torch torchvision torchaudio
RUN pip3 install transformers datasets accelerate librosa soundfile

RUN useradd -m -u 1000 lee

WORKDIR /app
USER lee

CMD ["python", "/app/main.py"]
