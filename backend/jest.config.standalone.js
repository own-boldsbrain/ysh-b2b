/**
 * Jest config for standalone tests (no Medusa dependencies)
 */

const config = {
  transform: {
    "^.+\\.[jt]s$": [
      "@swc/jest",
      {
        jsc: {
          parser: { syntax: "typescript", decorators: true },
          target: "es2022",
        },
      },
    ],
  },
  testEnvironment: "node",
  moduleFileExtensions: ["js", "ts", "json"],
  modulePathIgnorePatterns: ["dist/", ".medusa/server", ".medusa/admin"],
  testTimeout: 10000,
  testMatch: ["**/integration-tests/*standalone*.spec.[jt]s"],
  verbose: true,
  // NO setup files - standalone test
  setupFiles: [],
  setupFilesAfterEnv: [],
};

export default config;
