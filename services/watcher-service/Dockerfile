FROM golang:1.22-alpine AS build

WORKDIR /app

COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal

RUN go build -o /out/watcher-service ./cmd/watcher-service

FROM alpine:3.20

WORKDIR /app

COPY --from=build /out/watcher-service /usr/local/bin/watcher-service

EXPOSE 8081

ENTRYPOINT ["/usr/local/bin/watcher-service"]

