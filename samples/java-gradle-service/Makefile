# Makefile contract - Java / Gradle starter.
# build.gradle(.kts) needs: plugins { jacoco; checkstyle } (see samples/java-gradle-service)
#   jacocoTestReport { reports { xml.required = true } }, checkstyle { configFile = config/checkstyle.xml }
# Set component input coverage_format: jacoco (GitLab). Azure reads JaCoCo natively.
# Different JDKs (e.g. 17 and 21) = different build_image, same Makefile.
# Multi-module: add the jacoco-report-aggregation plugin and copy the aggregated XML instead.
# Corporate networks: set distributionUrl in gradle/wrapper/gradle-wrapper.properties to your mirror.
GRADLE := $(if $(wildcard ./gradlew),./gradlew,gradle) --no-daemon -q

.PHONY: setup lint test coverage build

setup:
	$(GRADLE) dependencies > /dev/null

lint:
	$(GRADLE) check -x test

test:
	$(GRADLE) test

coverage:
	$(GRADLE) test jacocoTestReport
	mkdir -p reports
	cp build/reports/jacoco/test/jacocoTestReport.xml reports/coverage.xml
	for f in build/test-results/test/TEST-*.xml; do cp "$$f" reports/junit-$$(basename "$$f"); done

build:
	$(GRADLE) assemble
	mkdir -p dist && cp build/libs/*.jar dist/
