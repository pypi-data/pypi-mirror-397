const jestJupyterLab = require('@jupyterlab/testutils/lib/jest-config');

// Provide a File implementation when Node.js doesn't expose it globally.
if (typeof File === 'undefined') {
  try {
    const { File: NodeFile } = require('node:buffer');
    if (NodeFile) {
      global.File = NodeFile;
    }
  } catch (error) {
    try {
      const { File: UndiciFile } = require('undici');
      if (UndiciFile) {
        global.File = UndiciFile;
      }
    } catch {
      // ignore; @jupyterlab/testing will fail loudly if File remains undefined
    }
  }
}

const esModules = [
  '@codemirror',
  '@jupyter/ydoc',
  '@jupyterlab/',
  'lib0',
  'nanoid',
  'vscode-ws-jsonrpc',
  'y-protocols',
  'y-websocket',
  'yjs'
].join('|');

const baseConfig = jestJupyterLab(__dirname);

module.exports = {
  ...baseConfig,
  automock: false,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/.ipynb_checkpoints/*'
  ],
  coverageReporters: ['lcov', 'text'],
  testRegex: 'src/.*/.*.spec.ts[x]?$',
  transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`]
};
