import sys
import time
import logging
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from patchright.async_api import async_playwright, Page, BrowserContext


@dataclass
class TurnstileResult:
    turnstile_value: Optional[str]
    elapsed_time_seconds: float
    status: str
    reason: Optional[str] = None


class CustomLogger(logging.Logger):
    COLORS = {
        'DEBUG': '\033[35m',  # Magenta
        'INFO': '\033[34m',  # Blue
        'SUCCESS': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
    }
    RESET = '\033[0m'  # Reset color

    def format_message(self, level, message):
        timestamp = time.strftime('%H:%M:%S')
        return f"[{timestamp}] [{self.COLORS.get(level, '')}{level}{self.RESET}] -> {message}"

    def debug(self, message, *args, **kwargs):
        super().debug(self.format_message('DEBUG', message), *args, **kwargs)

    def info(self, message, *args, **kwargs):
        super().info(self.format_message('INFO', message), *args, **kwargs)

    def success(self, message, *args, **kwargs):
        super().info(self.format_message('SUCCESS', message), *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        super().warning(self.format_message('WARNING', message), *args, **kwargs)

    def error(self, message, *args, **kwargs):
        super().error(self.format_message('ERROR', message), *args, **kwargs)


logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("TurnstileSolver")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class AsyncTurnstileSolver:
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Turnstile Solver</title>
        <script
          src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback"
          async=""
          defer=""
        ></script>
      </head>
      <body>
        <!-- cf turnstile -->
      </body>
    </html>
    """

    def __init__(self, debug: bool = False, headless: Optional[bool] = False, useragent: Optional[str] = None):
        self.debug = debug
        self.headless = headless
        self.useragent = useragent
        self.browser_args = [
            "--disable-blink-features=AutomationControlled",
        ]

        if self.useragent:
            self.browser_args.append(f"--user-agent={self.useragent}")

    async def _setup_page(self, context: BrowserContext, url: str, sitekey: str) -> Page:
        """Set up the page with Turnstile widget."""
        page = await context.new_page()
        url_with_slash = url + "/" if not url.endswith("/") else url

        if self.debug:
            logger.debug(f"Navigating to URL: {url_with_slash}")

        turnstile_div = f'<div class="cf-turnstile" data-sitekey="{sitekey}"></div>'
        page_data = self.HTML_TEMPLATE.replace("<!-- cf turnstile -->", turnstile_div)

        await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
        await page.goto(url_with_slash)

        return page

    async def _get_turnstile_response(self, page: Page, max_attempts: int = 10) -> Optional[str]:
        """Attempt to retrieve Turnstile response."""
        attempts = 0

        while attempts < max_attempts:
            turnstile_check = await page.eval_on_selector(
                "[name=cf-turnstile-response]",
                "el => el.value"
            )

            if turnstile_check == "":
                if self.debug:
                    logger.debug(f"Attempt {attempts + 1}: No Turnstile response yet.")

                await page.evaluate("document.querySelector('.cf-turnstile').style.width = '70px'")
                await page.click(".cf-turnstile")
                await asyncio.sleep(0.5)
                attempts += 1
            else:
                turnstile_element = await page.query_selector("[name=cf-turnstile-response]")
                if turnstile_element:
                    return await turnstile_element.get_attribute("value")
                break

        return None

    async def solve(self, url: str, sitekey: str) -> TurnstileResult:
        """
        Solve the Turnstile challenge and return the result.

        Args:
            url: The URL where the Turnstile challenge is hosted
            sitekey: The Turnstile sitekey
            headless: Whether to run the browser in headless mode

        Returns:
            TurnstileResult object containing the solution details
        """
        start_time = time.time()

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless, args=self.browser_args)
            context = await browser.new_context()

            try:
                page = await self._setup_page(context, url, sitekey)
                turnstile_value = await self._get_turnstile_response(page)

                elapsed_time = round(time.time() - start_time, 3)

                if not turnstile_value:
                    result = TurnstileResult(
                        turnstile_value=None,
                        elapsed_time_seconds=elapsed_time,
                        status="failure",
                        reason="Max attempts reached without token retrieval"
                    )
                    logger.error("Failed to retrieve Turnstile value.")
                else:
                    result = TurnstileResult(
                        turnstile_value=turnstile_value,
                        elapsed_time_seconds=elapsed_time,
                        status="success"
                    )
                    logger.success(f"Successfully solved captcha: {turnstile_value[:45]}... in {elapsed_time} seconds")

            finally:
                await context.close()
                await browser.close()

                if self.debug:
                    logger.debug(f"Elapsed time: {result.elapsed_time_seconds} seconds")
                    logger.debug("Browser closed. Returning result.")

        return result


async def get_turnstile_token(url: str, sitekey: str, headless: bool = False) -> Dict:
    """Legacy wrapper function for backward compatibility."""
    solver = AsyncTurnstileSolver(debug=False, headless=headless)
    result = await solver.solve(url=url, sitekey=sitekey)
    return result.__dict__


if __name__ == "__main__":
    result = asyncio.run(get_turnstile_token(
        url="https://bypass.city/",
        sitekey="0x4AAAAAAAGzw6rXeQWJ_y2P"
    ))
    print(result)
