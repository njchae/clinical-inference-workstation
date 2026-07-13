const { defineConfig } = require("@playwright/test");
const fs = require("fs");

const systemChromePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
const launchOptions = systemChromePath && fs.existsSync(systemChromePath)
  ? { executablePath: systemChromePath }
  : {};

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  outputDir: "output/playwright",
  use: {
    baseURL: "http://127.0.0.1:8000",
    launchOptions
  },
  webServer: {
    command: ".venv/bin/python scripts/run_api.py",
    url: "http://127.0.0.1:8000/health",
    reuseExistingServer: true,
    timeout: 30000
  }
});
