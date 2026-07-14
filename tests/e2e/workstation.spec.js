const { test, expect } = require("@playwright/test");

test("workstation should load recorded cases and update the review note", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Inference Review Workstation" })).toBeVisible();
  await expect(page.locator(".case-selector")).toHaveCount(3);

  await page.locator(".case-selector").first().click();
  await expect(page.locator("#review-note")).toContainText("Human review");
  await expect(page.locator("#signal-list")).toContainText("Recorded signal");
});

test("workstation should show the public-data and non-diagnostic scope", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".case-provenance")).toContainText("CC BY 4.0");
  await expect(page.locator("#review-note")).toContainText("not a clinical assessment");
});
