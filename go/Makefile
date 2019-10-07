.PHONY: all clean deps example

all: deps capi sink

clean:
	rm -f scion_api.so sink pyscion.pyc

deps:
	govendor sync -v

capi: scion_api.so

scion_api.so: scion_api.go
	go build -o scion_api.so -buildmode=c-shared scion_api.go

example: capi example.py
	@echo To test the API, run \"python3 example.py\"
	@echo To test the sink, run \"./sink\" and send data using e.g. netcat

sink: sink_src/sink.go
	cd sink_src && go build -o ../sink sink.go
