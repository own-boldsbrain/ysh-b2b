from playwright.sync_api import sync_playwright
import time

def run(playwright):

    time.sleep(60) # Wait for server to start

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://localhost:8000/us/kits-hibridos")
    page.screenshot(path="jules-scratch/verification/plp.png")

    page.locator('a:has-text("Medusa T-Shirt")').click()
    page.wait_for_load_state("networkidle")

    page.screenshot(path="jules-scratch/verification/pdp.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
