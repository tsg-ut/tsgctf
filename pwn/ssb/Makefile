BUILD_CONTAINER = gcc:4.9
dbuild: writeup/fs.c
	docker run -w $(PWD) -v $(PWD):$(PWD) -it ${BUILD_CONTAINER} make build -C writeup
.PHONY: dbuild
