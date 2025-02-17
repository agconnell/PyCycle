FROM ubuntu:latest

RUN mkdir -p /home/ubuntu/pycycle/
COPY . /home/ubuntu/pycycle/
WORKDIR /home/ubuntu/pycycle/

LABEL description="Python app for indoor cycling and maybe running"
LABEL version="1.0"
