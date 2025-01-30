FROM nvidia/cuda:12.1.1-devel-ubuntu22.04
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-pip python-is-python3 git

# Install NumPy 1.x first to avoid version conflicts
RUN pip3 install "numpy<2.0"

# Install PyTorch 2.1.2 with CUDA 12.1 support
RUN pip3 install --no-cache-dir torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121

RUN pip3 install transformers datasets accelerate librosa soundfile

RUN useradd -m -u 1000 lee

# Set up CUDA environment variables
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

WORKDIR /app
USER lee

CMD ["python", "/app/main.py"]
