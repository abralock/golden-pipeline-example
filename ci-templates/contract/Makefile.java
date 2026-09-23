# Makefile contract - Java / Maven starter.  Needs jacoco-maven-plugin in pom.xml.
# Set component input coverage_format: jacoco (GitLab). Azure reads JaCoCo natively.
.PHONY: setup lint test coverage build

setup:
	./mvnw -B -q dependency:go-offline

lint:
	./mvnw -B -q spotless:check checkstyle:check

test:
	./mvnw -B test

coverage:
	./mvnw -B verify jacoco:report
	mkdir -p reports
	cp target/site/jacoco/jacoco.xml reports/coverage.xml
	for f in target/surefire-reports/TEST-*.xml; do cp "$$f" reports/junit-$$(basename "$$f"); done

build:
	./mvnw -B -DskipTests package
	mkdir -p dist && cp target/*.jar dist/
