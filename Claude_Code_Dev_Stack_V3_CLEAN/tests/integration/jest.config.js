/**
 * Jest Configuration for Integration Testing
 * Tests TypeScript/JavaScript components across the entire stack
 */

export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  globals: {
    'ts-jest': {
      useESM: true
    }
  },
  moduleNameMapping: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      useESM: true
    }]
  },
  testMatch: [
    '<rootDir>/**/*.test.ts',
    '<rootDir>/**/*.test.js',
    '<rootDir>/**/*.integration.test.ts'
  ],
  collectCoverageFrom: [
    '../../core/**/*.{ts,js}',
    '../../apps/**/*.{ts,js,tsx}',
    '../../integrations/**/*.{ts,js}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/build/**'
  ],
  coverageDirectory: './coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/setup/jest.setup.ts'],
  testTimeout: 30000,
  maxWorkers: '50%',
  verbose: true,
  detectOpenHandles: true,
  forceExit: true,
  bail: false,
  errorOnDeprecated: true
};