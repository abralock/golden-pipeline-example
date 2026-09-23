// @ts-check
const eslint = require('@eslint/js');
const { defineConfig } = require('eslint/config');
const tseslint = require('typescript-eslint');
const angular = require('angular-eslint');

module.exports = defineConfig([
  { ignores: ['dist/', '.angular/', 'coverage/', 'reports/', 'eslint.config.js'] },
  {
    files: ['**/*.ts'],
    extends: [eslint.configs.recommended, tseslint.configs.strict, angular.configs.tsRecommended],
    processor: angular.processInlineTemplates,
    rules: {
      complexity: ['error', 8],
      '@angular-eslint/component-selector': ['error', { type: 'element', prefix: 'app', style: 'kebab-case' }],
    },
  },
  {
    files: ['**/*.html'],
    extends: [angular.configs.templateRecommended, angular.configs.templateAccessibility],
  },
]);
