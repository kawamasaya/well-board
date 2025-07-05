import prettier from 'eslint-config-prettier'
import vue from 'eslint-plugin-vue'
import typescriptParser from '@typescript-eslint/parser'
import vueParser from 'vue-eslint-parser'

export default [
  // TypeScript files
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
  },

  // Vue files
  {
    files: ['**/*.vue'],
    plugins: {
      vue,
    },
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        parser: typescriptParser,
      },
    },
    rules: {
      ...vue.configs.recommended.rules,
    },
  },

  // Ignore generated files
  {
    ignores: ['**/*.d.ts', 'dist/**', 'node_modules/**'],
  },

  // Prettier configuration
  prettier,
]
