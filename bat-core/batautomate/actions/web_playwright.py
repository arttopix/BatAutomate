import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, Playwright

from .base import BaseAction
from .registry import register_action
from ..models.context import ExecutionContext

logger = logging.getLogger("batautomate")


def _launch_browser_with_auto_install(pw: Playwright, headless: bool) -> Browser:
    try:
        return pw.chromium.launch(headless=headless)
    except Exception as e:
        err_msg = str(e)
        if "Executable doesn't exist" in err_msg or "Please run the following command" in err_msg:
            logger.info("Playwright Chromium browser not detected. Installing Chromium automatically (first run only)...")
            res = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
            if res.returncode != 0:
                raise RuntimeError(
                    "Failed to auto-install Chromium. Please run in terminal: playwright install chromium"
                ) from e
            try:
                return pw.chromium.launch(headless=headless)
            except Exception as retry_err:
                retry_msg = str(retry_err)
                if "Host system is missing dependencies" in retry_msg or "libraries" in retry_msg.lower():
                    raise RuntimeError(
                        "Chromium installed, but host system is missing OS dependencies. "
                        "Please run in terminal: sudo playwright install-deps chromium"
                    ) from retry_err
                raise
        elif "Host system is missing dependencies" in err_msg:
            raise RuntimeError(
                "Host system is missing dependencies to run Chromium. "
                "Please run in terminal: sudo playwright install-deps chromium"
            ) from e
        raise


def _get_page(context: ExecutionContext) -> Page:
    page = context.get_variable("__playwright_page__")
    if not page:
        raise RuntimeError("No active browser page found. Please execute 'web.open' first.")
    return page


def _resolve_locator(page: Page, parameters: Dict[str, Any]):
    selector = parameters.get("selector")
    label = parameters.get("label")

    if label:
        return page.locator(f"//label[normalize-space()='{label}']/following::input[1]")
    elif selector:
        return page.locator(selector)
    else:
        raise ValueError("Either 'selector' or 'label' parameter is required.")


@register_action("web.open")
class WebOpenAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        url = parameters.get("url")
        headless = bool(parameters.get("headless", False))
        timeout = float(parameters.get("timeout", 30000))

        pw: Optional[Playwright] = context.get_variable("__playwright_pw__")
        browser: Optional[Browser] = context.get_variable("__playwright_browser__")

        if not pw:
            pw = sync_playwright().start()
            context.set_variable("__playwright_pw__", pw)

        if not browser:
            browser = _launch_browser_with_auto_install(pw, headless=headless)
            context.set_variable("__playwright_browser__", browser)

        page = browser.new_page()
        page.set_default_timeout(timeout)
        context.set_variable("__playwright_page__", page)

        if url:
            page.goto(url, wait_until="networkidle")

        return {"url": url, "headless": headless, "status": "opened"}


@register_action("web.click")
class WebClickAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        page = _get_page(context)
        locator = _resolve_locator(page, parameters)
        locator.first.click()
        return {"action": "web.click", "status": "clicked"}


@register_action("web.type")
class WebTypeAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        page = _get_page(context)
        locator = _resolve_locator(page, parameters)
        text = str(parameters.get("text", ""))
        locator.first.fill(text)
        return {"action": "web.type", "text": text, "status": "typed"}


@register_action("web.get_text")
class WebGetTextAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        page = _get_page(context)
        locator = _resolve_locator(page, parameters)
        text = locator.first.inner_text()
        return text


@register_action("web.screenshot")
class WebScreenshotAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        page = _get_page(context)
        path_str = parameters.get("path", "screenshot.png")
        full_page = bool(parameters.get("full_page", False))

        target_path = Path(path_str)
        if not target_path.is_absolute():
            flow_dir_str = context.get_variable("__flow_dir__")
            if flow_dir_str:
                target_path = Path(flow_dir_str) / path_str

        target_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(target_path), full_page=full_page)
        return {"screenshot_path": str(target_path)}


@register_action("web.close")
class WebCloseAction(BaseAction):
    def execute(self, parameters: Dict[str, Any], context: ExecutionContext) -> Any:
        if context.get_variable("__shared_browser__"):
            logger.warning(
                "Safeguard: 'web.close' was invoked inside a subflow sharing parent browser session. "
                "Skipping browser closure to protect parent workflow."
            )
            return {"status": "skipped", "reason": "protected_shared_browser"}

        browser: Optional[Browser] = context.get_variable("__playwright_browser__")
        pw: Optional[Playwright] = context.get_variable("__playwright_pw__")

        if browser:
            browser.close()
            context.set_variable("__playwright_browser__", None)
            context.set_variable("__playwright_page__", None)

        if pw:
            pw.stop()
            context.set_variable("__playwright_pw__", None)

        return {"status": "closed"}
