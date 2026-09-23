# Makefile contract - Angular starter (tested with Angular 21, Vitest 4 - the default test runner since v21).
# devDependencies: @vitest/coverage-v8 (same version as vitest), angular-eslint, eslint, typescript-eslint
# Angular 22 needs Node >= 22.22.3 / 24.15 / 26.
# `npm ci` from the lockfile works on npm 10, but creating/changing dependencies (ng new, npm install)
# can fail on npm 10 with "Cannot read properties of null (reading 'edgesOut')" - developers use npm >= 11.
# Karma projects: migrate to Vitest (Angular guide "Migrating from Karma to Vitest"), or use
# karma-junit-reporter + karma-coverage (type: cobertura) and write the same two report files.
# --coverage-include lists ALL app files: without it, files no test imports are tree-shaken out of the
#   test build and never appear in the report (the platform check fails the MR if that happens).
#   Code that nothing imports at all (dead code) is still invisible - catch it with a dead-code tool.
# Keep business logic in services/plain TS (src/app/**), not in templates, so it is unit-testable.
PROJECT := $(shell node -p "Object.keys(require('./angular.json').projects)[0]" 2>/dev/null)

.PHONY: setup lint test coverage build

setup:
	npm ci

lint:
	npx eslint . --max-warnings=0
	npx tsc -p tsconfig.app.json --noEmit
	npx tsc -p tsconfig.spec.json --noEmit

test:
	npx ng test --watch=false

coverage:
	rm -rf reports coverage && mkdir -p reports
	npx ng test --watch=false --coverage \
	  --coverage-include='src/app/**/*.ts' --coverage-exclude='src/app/**/*.spec.ts' \
	  --coverage-exclude='src/app/app.config.ts' \
	  --coverage-reporters=cobertura --coverage-reporters=text-summary \
	  --reporters=junit --reporters=default --output-file=reports/junit.xml
	cp coverage/$(PROJECT)/cobertura-coverage.xml reports/coverage.xml

build:
	npx ng build --configuration production
	# output: dist/$(PROJECT)/browser
