FROM golang:1.20-alpine as builder

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /go/bin/app .

FROM gcr.io/distroless/static-debian11 as prod

COPY --from=builder /go/bin/app /

EXPOSE 8080

USER 1000:1000
