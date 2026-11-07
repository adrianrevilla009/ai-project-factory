// Example ESLint flat-config fragment for a generated React project (ESLint 9 flat config; TODO-VERIFY version).
// Complements dependency-cruiser.example.cjs: ESLint gives feedback in the editor, depcruise gates CI.
export default [
  {
    files: ['src/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': ['error', {
        patterns: [
          // Only the public API (index.ts) of a feature may be imported from outside it.
          { group: ['@/features/*/*'], message: 'Import from "@/features/<name>" (its index.ts) only.' },
          // No relative escapes out of a feature or shared folder.
          { group: ['../../../*'], message: 'Use the "@/" alias, not deep relative paths.' },
        ],
      }],
    },
  },
  {
    // Inside a feature, its own internals are free to import each other.
    files: ['src/features/**/*.{ts,tsx}'],
    rules: { 'no-restricted-imports': 'off' },
  },
];
