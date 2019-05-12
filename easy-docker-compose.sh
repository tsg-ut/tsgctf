# plz execute /bin/sh easy-docker-compose.sh [ARGS] for Container Optimized OS

if [ $# -lt 1 ]; then
    echo 'command?'
    exit 1
fi

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.24.0 "$@"
