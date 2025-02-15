import sys
import time
import logging
import asyncio
import argparse
from typing import Optional
from collections import deque
from dataclasses import dataclass
from quart import Quart, request, jsonify
from patchright.async_api import async_playwright


class CustomLogger(logging.Logger):
    COLORS = {
        'DEBUG': '\033[35m',    # Magenta
        'INFO': '\033[34m',     # Blue
        'SUCCESS': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
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
logger = logging.getLogger("TurnstileAPIServer")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


@dataclass
class TurnstileAPIResult:
    result: Optional[str]
    elapsed_time_seconds: Optional[float] = None
    status: str = "success"
    error: Optional[str] = None


class PagePool:
    def __init__(self, context, debug: bool = False, log=None):
        self.context = context
        self.min_size = 1
        self.max_size = 10
        self.available_pages: deque = deque()
        self.in_use_pages: set = set()
        self._lock = asyncio.Lock()
        self.debug = debug
        self.log = log

    async def initialize(self):
        """Create initial pool of pages"""
        for _ in range(self.min_size):
            page = await self.context.new_page()
            self.available_pages.append(page)

    async def get_page(self):
        """Get an available page from the pool or create a new one if needed"""
        async with self._lock:
            if (not self.available_pages and
                    len(self.in_use_pages) < self.max_size):
                page = await self.context.new_page()
                if self.debug:
                    self.log.debug(f"Created new page. Total pages: {len(self.in_use_pages) + 1}")
            else:
                while not self.available_pages:
                    await asyncio.sleep(0.1)
                page = self.available_pages.popleft()

            self.in_use_pages.add(page)
            return page

    async def return_page(self, page):
        """Return a page to the pool or close it if we have too many"""
        async with self._lock:
            self.in_use_pages.remove(page)
            total_pages = len(self.available_pages) + len(self.in_use_pages) + 1
            if total_pages > self.min_size and len(self.available_pages) >= 2:
                await page.close()
                if self.debug:
                    self.log.debug(f"Closed excess page. Total pages: {total_pages - 1}")
            else:
                self.available_pages.append(page)


class TurnstileAPIServer:
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Turnstile Solver</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" 
                async="" defer=""></script>
    </head>
    <body>
        <!-- cf turnstile -->
    </body>
    </html>
    """

    def __init__(self, debug: bool = False, headless: Optional[bool] = None, useragent: Optional[str] = None):
        self.app = Quart(__name__)
        self.debug = debug
        self.headless = headless
        self.useragent = useragent
        self.page_pool = None
        self.browser = None
        self.context = None
        self.browser_args = [
            "--disable-blink-features=AutomationControlled",
        ]

        if self.headless is None:
            logger.warning("Headless mode not set, defaulting to False.")
            self.headless = False

        if self.useragent:
            self.browser_args.append(f"--user-agent={self.useragent}")

        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up the application routes."""
        self.app.before_serving(self._startup)
        self.app.route('/turnstile', methods=['GET'])(self.process_turnstile)
        self.app.route('/')(self.index)

    async def _startup(self) -> None:
        """Initialize the browser and page pool on startup."""
        logger.debug("Starting browser initialization...")
        try:
            await self._initialize_browser()
            logger.info("Browser and page pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def _initialize_browser(self) -> None:
        """Initialize the browser and create the page pool."""
        if self.debug:
            logger.debug("Initializing browser with automation-resistant arguments...")

        playwright = await async_playwright().start()

        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=self.browser_args
        )

        self.context = await self.browser.new_context()
        self.page_pool = PagePool(
            self.context,
            debug=self.debug
        )
        await self.page_pool.initialize()

        if self.debug:
            logger.debug(f"Browser and page pool initialized (min: {self.page_pool.min_size}, max: {self.page_pool.max_size})")

    async def _solve_turnstile(self, url: str, sitekey: str) -> TurnstileAPIResult:
        """Solve the Turnstile challenge."""
        start_time = time.time()

        page = await self.page_pool.get_page()
        try:
            if self.debug:
                logger.debug(f"Starting Turnstile solve for URL: {url}")
                logger.debug("Setting up page data and route")

            url_with_slash = url + "/" if not url.endswith("/") else url
            turnstile_div = f'<div class="cf-turnstile" data-sitekey="{sitekey}"></div>'
            page_data = self.HTML_TEMPLATE.replace("<!-- cf turnstile -->", turnstile_div)

            await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
            await page.goto(url_with_slash)

            if self.debug:
                logger.debug("Setting up Turnstile widget dimensions")

            await page.eval_on_selector(
                "//div[@class='cf-turnstile']",
                "el => el.style.width = '70px'"
            )

            if self.debug:
                logger.debug("Starting Turnstile response retrieval loop")

            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                try:
                    turnstile_check = await page.input_value("[name=cf-turnstile-response]")
                    if turnstile_check == "":
                        attempts += 1
                        if self.debug:
                            logger.debug(f"Attempt {attempts + 1}: No Turnstile response yet")

                        await page.click("//div[@class='cf-turnstile']", timeout=3000)
                        await asyncio.sleep(0.5)
                    else:
                        element = await page.query_selector("[name=cf-turnstile-response]")
                        if element:
                            value = await element.get_attribute("value")
                            elapsed_time = round(time.time() - start_time, 3)

                            if self.debug:
                                logger.debug(f"Turnstile response received: {value[:45]}...")

                            logger.success(f"Successfully solved captcha: {value[:10]}... in {elapsed_time} Seconds")

                            return TurnstileAPIResult(
                                result=value,
                                elapsed_time_seconds=elapsed_time
                            )
                        break
                except:
                    pass

            logger.error("Failed to retrieve Turnstile value")
            return TurnstileAPIResult(
                result=None,
                status="failure",
                error="Max attempts reached without solution"
            )

        except Exception as e:
            logger.error(f"Error solving Turnstile: {str(e)}")
            return TurnstileAPIResult(
                result=None,
                status="error",
                error=str(e)
            )
        finally:
            if self.debug:
                logger.debug("Clearing page state")
            await page.goto("about:blank")
            await self.page_pool.return_page(page)

    async def process_turnstile(self):
        """Handle the /turnstile endpoint requests."""
        url = request.args.get('url')
        sitekey = request.args.get('sitekey')

        if not url or not sitekey:
            logger.warning("Missing required parameters: 'url' or 'sitekey'")
            return jsonify({
                "status": "error",
                "error": "Both 'url' and 'sitekey' are required"
            }), 400

        if self.debug:
            logger.debug(f"Processing request for URL: {url}")
        try:
            result = await self._solve_turnstile(url=url, sitekey=sitekey)
            if self.debug:
                logger.debug(f"Request completed with status: {result.status}")
            return jsonify(result.__dict__), 200 if result.status == "success" else 500
        except Exception as e:
            logger.error(f"Unexpected error processing request: {str(e)}")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500


    async def index(self):
        """Serve the API documentation page."""
        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Turnstile Solver API</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-900 text-gray-200 min-h-screen flex items-center justify-center">
                <div class="bg-gray-800 p-8 rounded-lg shadow-md max-w-2xl w-full border border-red-500">
                    <h1 class="text-3xl font-bold mb-6 text-center text-red-500">Welcome to Turnstile Solver API</h1>
            
                    <p class="mb-4 text-gray-300">To use the turnstile service, send a GET request to 
                       <code class="bg-red-700 text-white px-2 py-1 rounded">/turnstile</code> with the following query parameters:</p>
            
                    <ul class="list-disc pl-6 mb-6 text-gray-300">
                        <li><strong>url</strong>: The URL where Turnstile is to be validated</li>
                        <li><strong>sitekey</strong>: The site key for Turnstile</li>
                    </ul>
            
                    <div class="bg-gray-700 p-4 rounded-lg mb-6 border border-red-500">
                        <p class="font-semibold mb-2 text-red-400">Example usage:</p>
                        <code class="text-sm break-all text-red-300">/turnstile?url=https://example.com&sitekey=sitekey</code>
                    </div>
            
                    <div class="bg-red-900 border-l-4 border-red-600 p-4 mb-6">
                        <p class="text-red-200 font-semibold">This project is inspired by 
                           <a href="https://github.com/Body-Alhoha/turnaround" class="text-red-300 hover:underline">Turnaround</a> 
                           and is currently maintained by 
                           <a href="https://github.com/Theyka" class="text-red-300 hover:underline">Theyka</a> 
                           and <a href="https://github.com/sexfrance" class="text-red-300 hover:underline">Sexfrance</a>.</p>
                    </div>
                </div>
            </body>
            </html>
        """


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Turnstile API Server")

    parser.add_argument('--headless', type=bool, default=False, help='Run browser in headless mode (default: True)')
    parser.add_argument('--useragent', type=str, default=None, help='Set custom user agent for the browser')
    parser.add_argument('--debug', type=str, default=False, help='Enable/Disable debug mode (default: False)')
    return parser.parse_args()


def create_app(debug: bool, headless: bool, useragent: Optional[str] = None) -> Quart:
    server = TurnstileAPIServer(debug=debug, headless=headless, useragent=useragent)
    return server.app


if __name__ == '__main__':
    args = parse_args()

    app = create_app(debug=args.debug, headless=args.headless, useragent=args.useragent)
    app.run()

# Credits for the changes: github.com/sexfrance
# Credit for the original script: github.com/Theyka
