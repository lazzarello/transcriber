# Transcriber

## A realtime speech transcription system

This project runs as a container with the nvidia runtime to use a GPU accelerated Whisper Large v3 model. Development is set up with the VS Code Dev Containers extension.

## Sending messages to the container

The engine container runs with a UNIX socket exposed to allow data to stream back and forth between the host and container.

The client, in this case a UI using the curses terminal UI library, sends messages to the container over the socket.

`docker run --rm -it -v $(pwd):/app socket-server`

## TODO

* Audio input from microphone to record to a file on disk
* Create an architecture and design document
* Should the UI manage the Pipewire graph and send chunks over to the engine in the container, who then sends back a data structure with the text output?
* Can the text output just be a stream that writes to a file on disk?
