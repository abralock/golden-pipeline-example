/** Coverage scope is reviewed by the platform team (CODEOWNERS): business logic and
 *  components are measured; app/ route files are thin and covered by E2E tests instead. */
const nextJest = require("next/jest");

const createJestConfig = nextJest({ dir: "./" });

module.exports = createJestConfig({
  testEnvironment: "jsdom",
  moduleNameMapper: { "^@/(.*)$": "<rootDir>/$1" },
  collectCoverageFrom: ["lib/**/*.{ts,tsx}", "components/**/*.{ts,tsx}"],
  coverageProvider: "v8",
});
