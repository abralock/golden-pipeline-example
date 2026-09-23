# Makefile contract - Java / Maven starter.
# pom.xml needs: jacoco-maven-plugin (prepare-agent + report in verify, XML format),
#                maven-checkstyle-plugin with config/checkstyle.xml (complexity <= 8).
# Set component input coverage_format: jacoco (GitLab). Azure reads JaCoCo natively.
# Different JDKs (e.g. 17 and 21) = different build_image, same Makefile.
# Corporate networks: point Maven at Artifactory/Nexus via settings.xml in the build image.
# Multi-module: add a report-aggregate module and copy its jacoco.xml instead.
MVN := $(if $(wildcard ./mvnw),./mvnw,mvn) -B -q

.PHONY: setup lint test coverage build

setup:
	$(MVN) dependency:go-offline

lint:
	$(MVN) checkstyle:check

test:
	$(MVN) test

coverage:
	$(MVN) verify
	mkdir -p reports
	cp target/site/jacoco/jacoco.xml reports/coverage.xml
	for f in target/surefire-reports/TEST-*.xml; do cp "$$f" reports/junit-$$(basename "$$f"); done

build:
	$(MVN) -DskipTests package
	mkdir -p dist && cp target/*.jar dist/
