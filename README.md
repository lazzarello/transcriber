# Transcriber

## A realtime speech transcription system

This project runs as a container with the nvidia runtime to use a GPU accelerated Whisper Large v3 model. Development is set up with the VS Code Dev Containers extension.

## TODO

* Audio input from microphone into dev container
* How will a UI work? Make a design document for that
* Can the container just be an "engine" with an API to a user interface that manages the Pipewire graph?
* Should the UI manage the Pipewire graph and send chunks over to the engine in the container, who then sends back a data structure with the text output?
* Can the text output just be a stream that writes to a file on disk?
