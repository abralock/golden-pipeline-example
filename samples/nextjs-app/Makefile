# Makefile contract - Next.js starter (tested with Next.js 16, React 19, Jest 30).
# devDependencies: jest, jest-environment-jsdom, jest-junit, @testing-library/react,
#                  @testing-library/dom, eslint@9, eslint-config-next
#   (eslint-plugin-react, used by eslint-config-next, does not support ESLint 10 yet.)
# jest.config.js: use next/jest, coverageProvider "v8", and collectCoverageFrom
#   ["lib/**", "components/**"]. Keep business logic in lib/ so it can be unit-tested.
#   Changes to collectCoverageFrom are reviewed by the platform team (CODEOWNERS).
# E2E tests (Playwright) cover app/ routes but run separately; they don't count toward the 80%.
# `next lint` was removed in Next.js 16, so ESLint is called directly.
# next.config.mjs must set output: "standalone" for the build target below.
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
	NEXT_TELEMETRY_DISABLED=1 npx next build
	rm -rf dist && mkdir -p dist/.next
	cp -r .next/standalone/. dist/
	cp -r .next/static dist/.next/static
	[ ! -d public ] || cp -r public dist/public
