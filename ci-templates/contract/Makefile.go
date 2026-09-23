# Makefile contract - Go starter.
# JUnit via go-junit-report, Cobertura via gocover-cobertura (both installed by `make setup`).
# Recommended: put golangci-lint (with gocyclo/gocognit enabled) in the platform Go build image
# and add `golangci-lint run` to lint.
# Corporate networks: set GOPROXY to your internal proxy (e.g. Artifactory) in the build image.
# Services keep binaries in cmd/<name>/main.go; library-only repos can make build = `go build ./...`.
GOBIN := $(shell go env GOPATH)/bin

.PHONY: setup lint test coverage build

setup:
	go mod download
	go install github.com/jstemmer/go-junit-report/v2@v2.1.0
	go install github.com/boumenot/gocover-cobertura@v1.3.0

lint:
	@test -z "$$(gofmt -l .)" || (echo "gofmt needed:"; gofmt -l .; exit 1)
	go vet ./...

test:
	go test ./...

coverage:
	mkdir -p reports
	go test -v -coverprofile=reports/cover.out -covermode=atomic ./... 2>&1 \
	  | $(GOBIN)/go-junit-report -set-exit-code -iocopy -out reports/junit.xml
	$(GOBIN)/gocover-cobertura -by-files < reports/cover.out > reports/coverage.xml

build:
	mkdir -p dist
	CGO_ENABLED=0 go build -trimpath -o dist/ ./cmd/...
