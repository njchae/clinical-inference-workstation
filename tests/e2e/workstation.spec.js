const { test, expect } = require("@playwright/test");

test("workstation should load sample cards and update the decision summary", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Synthetic Triage Workstation" })).toBeVisible();
  await expect(page.locator(".sample-card")).toHaveCount(3);

  await page.locator(".sample-card").first().click();
  await expect(page.locator("#decision-summary")).toContainText("based on combined visual signals");
  await expect(page.locator("#signal-list")).toContainText("Redness ratio");
});

test("workstation should analyze an uploaded sample image", async ({ page }) => {
  await page.goto("/");

  await page.locator("#upload-input").setInputFiles("web/samples/case-0042.png");
  await expect(page.locator("#decision-summary")).toContainText("based on combined visual signals");
  await expect(page.locator("#signal-list")).toContainText("Model probability");
});
