/* Example dependency-cruiser config for a generated React project (layout: src/app, src/features, src/shared).
 * Copy to the project root as .dependency-cruiser.cjs. Run: npx depcruise src --config .dependency-cruiser.cjs
 * Rule syntax: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md (TODO-VERIFY version) */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      from: {},
      to: { circular: true },
    },
    {
      name: 'shared-must-not-import-features-or-app',
      severity: 'error',
      from: { path: '^src/shared' },
      to: { path: '^src/(features|app)' },
    },
    {
      name: 'features-must-not-import-app',
      severity: 'error',
      from: { path: '^src/features' },
      to: { path: '^src/app' },
    },
    {
      // A feature may not reach into another feature at all; compose them in src/app or a page.
      name: 'no-cross-feature-imports',
      severity: 'error',
      from: { path: '^src/features/([^/]+)/' },
      to: { path: '^src/features/([^/]+)/', pathNot: '^src/features/$1/' },
    },
    {
      name: 'no-test-code-in-prod-code',
      severity: 'error',
      from: { path: '^src', pathNot: '\\.(test|spec|stories)\\.(ts|tsx)$|^src/test' },
      to: { path: '\\.(test|spec|stories)\\.(ts|tsx)$|^src/test' },
    },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.json' },
    doNotFollow: { path: 'node_modules' },
  },
};
