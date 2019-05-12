FROM ubuntu:18.04

RUN apt-get update && \
        apt-get -y upgrade && \
        apt-get install -y \
            xinetd \
            iproute2

RUN groupadd -r user && useradd -r -g user user

COPY --chown=root:root ./build/ctf.conf /etc/xinetd.d/ctf
COPY --chown=root:user ./build/flag /home/user/flag
COPY --chown=root:user ./build/start.sh /home/user/start.sh
COPY --chown=root:user ./problem/stlc /home/user/stlc
COPY --chown=root:user ./problem/libc-2.27.so /home/user/libc-2.27.so

WORKDIR /home/user

RUN chmod 444 /etc/xinetd.d/ctf && \
    chmod 444 flag && \
    chmod 555 ./stlc && \
    chmod 555 ./start.sh && \
    chmod 555 ./libc-2.27.so

USER user
EXPOSE 30007

CMD ["xinetd", "-dontfork"]
