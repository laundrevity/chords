FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y build-essential cmake python3-dev python3-pip gdb openssh-server vim fish && \
    apt update -qq && apt install -y python3.10-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install music21 MIDIUtil
RUN pip install flask
