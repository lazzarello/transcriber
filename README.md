# Transcriber

## A realtime speech transcription system

Transcriber uses a GPU accelerated Whisper Large v3 model. The transcription engine runs in a large container based on the 12.4.0-devel-ubuntu22.04 image from nvidia/cuda. This ensures the matrix of dependencies to get PyTorch to work is met. It also prevents accidently breaking the host system by fiddling with CUDA and Nvidia drivers.

The transcriber depends on streaming audio from a microphone. It does not work on recorded files.

## Sending messages to the container

The client is a UI using the curses terminal UI library, it sends messages to the container over the socket.

The engine container runs with a UNIX socket exposed to allow data to stream back and forth between the host and container. The nvidia-containter-toolkit must be installed and configured.

`docker run --rm -it --gpus all -v $(pwd):/app socket-server`

## TODO

* Audio input from microphone to record to a file on disk
* Create an architecture and design document
* Should the UI manage the Pipewire graph and send chunks over to the engine in the container, who then sends back a data structure with the text output? [It looks like this is possible](https://stackoverflow.com/a/75775875)
* Can the text output just be a stream that writes to a file on disk?
