import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  { rules: { complexity: ["error", 8] } },
  globalIgnores([".next/**", "dist/**", "reports/**", "coverage/**", "next-env.d.ts", "jest.config.js"]),
]);
