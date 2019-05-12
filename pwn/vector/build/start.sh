#!/bin/sh

LD_PRELOAD=/home/user/libc-2.27.so stdbuf -i0 -o0 -e0 /home/user/vector
