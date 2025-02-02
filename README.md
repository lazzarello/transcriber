# Transcriber

## A realtime speech transcription system

Transcriber uses a GPU accelerated Whisper Large v3 model. The transcription engine runs in a large container based on the 12.4.0-devel-ubuntu22.04 image from nvidia/cuda. This ensures the matrix of dependencies to get PyTorch to work is met. It also prevents accidently breaking the host system by fiddling with CUDA and Nvidia drivers.

The transcriber depends on streaming audio from a microphone. It does not work on recorded files.

## Architecture

See [Transcriber architecture.pdf](Transcriber architecture.pdf) for the first draft of the architecture.

## Sending messages to the container

The client is a UI using the curses terminal UI library, it sends messages to the container over the socket.

The engine container runs with a UNIX socket exposed to allow data to stream back and forth between the host and container. The nvidia-containter-toolkit must be installed and configured to get GPU acceleration for the Whisper model.

`docker run --rm -it --gpus all -v $(pwd):/app socket-server`

## TODO

* Add pipewire source node selector
* Add pipewire sink selector (defaults to built-in audio)

## BIG UPS!

* [Random user on the internet named Alex](https://stackoverflow.com/a/75775875) who figured out the pipewire socket into a container pattern for audio intput into the engine container