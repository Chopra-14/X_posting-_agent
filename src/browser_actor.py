import os
import json
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class SocialMediaActor:
    """Playwright automation for the mock social server.

    Handles session state persistence (cookies/local storage) to avoid
    re‑logging on every run.
    """

    def __init__(self, state_file: str = "data/browser_state.json"):
        self.state_file = Path(state_file)
        self.base_url = os.getenv("MOCK_SOCIAL_URL", "http://localhost:8080")
        self.username = os.getenv("MOCK_USERNAME", "demo_user")
        self.password = os.getenv("MOCK_PASSWORD", "demo_pass")

    def _save_state(self, context) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(self.state_file))

    def _load_state(self, browser) -> Optional[object]:
        if self.state_file.is_file():
            return browser.new_context(storage_state=str(self.state_file))
        return None

    def _login(self, page) -> bool:
        try:
            page.goto(f"{self.base_url}/login")
            page.fill("#username", self.username)
            page.fill("#password", self.password)
            page.click("#login-btn")
            page.wait_for_load_state("networkidle", timeout=5000)
            return True
        except PlaywrightTimeoutError:
            print("[ERROR] Login page timeout or missing selectors.")
            return False

    def _ensure_context(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = self._load_state(browser)
        if context is None:
            context = browser.new_context()
            page = context.new_page()
            if not self._login(page):
                # Clean up before exiting
                context.close()
                browser.close()
                playwright.stop()
                return None, None, None, None
            # Save session for future runs
            self._save_state(context)
        else:
            page = context.new_page()
        return playwright, browser, context, page

    def post_content(self, text: str) -> bool:
        """Post *text* to the compose page. Returns ``True`` on success."""
        playwright, browser, context, page = self._ensure_context()
        if not all([playwright, browser, context, page]):
            return False
        try:
            page.goto(f"{self.base_url}/compose/tweet")
            page.fill("#tweet-text", text)
            page.click("#post-btn")
            page.wait_for_load_state("networkidle", timeout=5000)
            success = True
        except PlaywrightTimeoutError:
            print("[ERROR] Compose page timeout or missing selectors.")
            success = False
        finally:
            context.close()
            browser.close()
            playwright.stop()
        return success