# Generate protoc files

```shell
    protoc --go_out=./grpc --go_opt=paths=import \
        --go-grpc_out=./grpc --go-grpc_opt=paths=import \
        proto/*.proto
```
