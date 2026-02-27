from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Go to the home page
        print("Navigating to home page...")
        page.goto("http://127.0.0.1:5000/")
        page.screenshot(path="verification/home.png")
        print("Home page screenshot taken.")

        # Go to Sign Up
        print("Navigating to Sign Up...")
        page.goto("http://127.0.0.1:5000/auth/signup")
        page.screenshot(path="verification/signup.png")
        print("Sign Up page screenshot taken.")

        # Go to Login
        print("Navigating to Login...")
        page.goto("http://127.0.0.1:5000/auth/login")
        page.screenshot(path="verification/login.png")
        print("Login page screenshot taken.")

    except Exception as e:
        print(f"Error: {e}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
