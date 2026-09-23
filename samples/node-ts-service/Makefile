# Makefile contract - Node.js / TypeScript (Jest) starter.
# devDependencies: typescript, jest, ts-jest, @types/jest, jest-junit, eslint, typescript-eslint
# ESLint rule `complexity: ["error", 8]` is the complexity limit (a SOLID proxy).
# Using Vitest instead of Jest? coverage target becomes:
#   npx vitest run --coverage.enabled --coverage.reporter=cobertura --coverage.reportsDirectory=reports \
#     --reporter=default --reporter=junit --outputFile.junit=reports/junit.xml
#   mv reports/cobertura-coverage.xml reports/coverage.xml
.PHONY: setup lint test coverage build

setup:
	npm ci

lint:
	npx eslint . --max-warnings=0
	npx tsc --noEmit

test:
	npx jest

coverage:
	mkdir -p reports
	JEST_JUNIT_OUTPUT_DIR=reports JEST_JUNIT_OUTPUT_NAME=junit.xml \
	  npx jest --ci --coverage --coverageReporters=cobertura --coverageReporters=text \
	  --coverageDirectory=reports --reporters=default --reporters=jest-junit
	mv reports/cobertura-coverage.xml reports/coverage.xml

build:
	rm -rf dist
	npx tsc -p tsconfig.build.json
