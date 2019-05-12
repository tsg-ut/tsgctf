FROM ubuntu:18.04
RUN apt update

RUN apt install make -y
RUN apt install vim -y
RUN apt install gcc -y
RUN apt install curl -y
RUN apt install libperl5.26 -y

COPY flag.txt /tmp/
WORKDIR /tmp/
