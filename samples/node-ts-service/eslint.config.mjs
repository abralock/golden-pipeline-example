import js from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig([
  { ignores: ["dist/", "reports/", "coverage/", "jest.config.js"] },
  js.configs.recommended,
  tseslint.configs.strict,
  { rules: { complexity: ["error", 8] } },
]);
