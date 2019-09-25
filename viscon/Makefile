.PHONY: all clean deps example

all: capi sink

clean:
	rm -f scion_api.so sink

deps:
	govendor sync -v

capi: scion_api.so

scion_api.so: scion_api.go
	go build -o scion_api.so -buildmode=c-shared scion_api.go

example: capi example.py
	@echo To test the API, run \"python3 example.py\"
	@echo To test the sink, run \"./sink\" and send data using e.g. netcat

sink: sink.go
	go build -o sink sink.go
