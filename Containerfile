# The fovea keeper: the keeper program, the released fovea verifier it checks
# every record with, and keep.sh, its one run. Signed in CI; the keeper's machine
# runs it by digest.
FROM docker.io/library/golang:1.27.0@sha256:4013ae0f9e7994f8535c58c811f8f863fbed38b72e0d51e6592156f758d66146 AS build
ARG FOVEA_VERSION=v0.3.0
ENV CGO_ENABLED=0 GOFLAGS=-trimpath
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
RUN go vet ./... && go build -o /out/keeper . \
 && GOBIN=/out go install "github.com/macula-io/macula-fovea/cli/cmd/fovea@${FOVEA_VERSION}"

FROM docker.io/library/alpine:3.22@sha256:5291449c3df73caf6ed85e649dec1b9e818b39a5d8c871e97afc13e9cd5e8fa8
ARG REVISION=unknown
LABEL org.opencontainers.image.source=https://github.com/macula-io/mcl-fovea-keeper \
      org.opencontainers.image.revision=${REVISION}
RUN apk add --no-cache git openssh-client ca-certificates
COPY --from=build /out/keeper /out/fovea /usr/local/bin/
COPY keep.sh /usr/local/bin/keep
ENTRYPOINT ["/usr/local/bin/keep"]
