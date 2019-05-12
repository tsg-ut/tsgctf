BUILD_CONTAINER = gcc:8.3
dbuild:
	docker run -w $(PWD) -v $(PWD):$(PWD) -it ${BUILD_CONTAINER} make build -C writeup
.PHONY: dbuild
