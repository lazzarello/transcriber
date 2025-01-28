# Use a base image with a lightweight Linux distribution
FROM ubuntu:latest

# Install PipeWire and other dependencies
RUN apt-get update && \
    apt-get install -y pipewire pipewire-audio-client-libraries pipewire-pulse

# Copy the PipeWire configuration files if needed
# COPY pipewire.conf /etc/pipewire/pipewire.conf
# COPY pipewire-pulse.conf /etc/pipewire/pipewire-pulse.conf

# RUN useradd -m -u 1000 lee
# USER lee
# Set environment variables
ENV PIPEWIRE_RUNTIME_DIR=/run/user/1000

# Expose the necessary ports or sockets
EXPOSE 4713

# Start PipeWire
CMD ["pipewire"]