import js from '@eslint/js'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'

// What the type checker cannot catch: hook rules, unsound escapes from the type system,
// and anything that would break the dev server's fast refresh.
export default tseslint.config(
  // The generated contract is not ours to style; it is regenerated, never edited.
  { ignores: ['dist', 'src/api/schema.d.ts'] },
  js.configs.recommended,
  {
    // The typed rules need a program, so they only apply to what a tsconfig includes.
    files: ['**/*.{ts,tsx}'],
    extends: [
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactHooks.configs.flat['recommended-latest'],
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      // A number in a message is unambiguous; spelling out String() around every status
      // code buys nothing.
      '@typescript-eslint/restrict-template-expressions': ['error', { allowNumber: true }],
    },
  },
  {
    files: ['src/**/*.tsx'],
    plugins: { 'react-refresh': reactRefresh },
    rules: { 'react-refresh/only-export-components': 'error' },
  },
)
