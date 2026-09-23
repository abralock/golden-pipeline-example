/** Coverage scope is reviewed by the platform team (CODEOWNERS).
 *  coverageProvider "v8": the default babel/istanbul path writes broken file paths with
 *  ts-jest + TypeScript 6, which silently disables the new-code check. */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/test"],
  collectCoverageFrom: ["src/**/*.ts"],
  coverageProvider: "v8",
};
