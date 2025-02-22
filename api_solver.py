import os
import sys
import time
import uuid
import json
import random
import string
import logging
import asyncio
import argparse
from quart import Quart, request, jsonify
from patchright.async_api import async_playwright


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
logger = logging.getLogger("TurnstileAPIServer")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class TurnstileAPIServer:
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Turnstile Solver</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" 
                async></script>
    </head>
    <body>
        <!-- cf turnstile -->
    </body>
    </html>
    """

    def __init__(self, headless: bool, useragent: str, debug: bool, persistent: bool, thread: int):
        self.app = Quart(__name__)
        self.debug = debug
        self.results = self._load_results()
        self.persistent = persistent
        self.headless = headless
        self.useragent = useragent
        self.thread_count = thread
        self.browser_pool = asyncio.Queue()
        self.browser_args = []
        if useragent:
            self.browser_args.append(f"--user-agent={useragent}")

        self._setup_routes()

    @staticmethod
    def _load_results():
        """Load previous results from results.json."""
        try:
            if os.path.exists("results.json"):
                with open("results.json", "r") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading results: {str(e)}. Starting with an empty results dictionary.")
        return {}

    def _save_results(self):
        """Save results to results.json."""
        try:
            with open("results.json", "w") as result_file:
                json.dump(self.results, result_file, indent=4)
        except IOError as e:
            logger.error(f"Error saving results to file: {str(e)}")

    def _setup_routes(self) -> None:
        """Set up the application routes."""
        self.app.before_serving(self._startup)
        self.app.route('/turnstile', methods=['GET'])(self.process_turnstile)
        self.app.route('/result', methods=['GET'])(self.get_result)
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
            logger.debug("Initializing browser with arguments...")

        playwright = await async_playwright().start()
        for _ in range(self.thread_count):
            if self.persistent:
                browser = await playwright.chromium.launch_persistent_context(
                    user_data_dir=f"{os.getcwd()}/tmp/turnstile-chrome-{''.join(random.choices(string.ascii_letters + string.digits, k=10))}",
                    channel="chrome",
                    headless=self.headless,
                    no_viewport=True,
                )
                context = None
                page = browser.pages[0]
            else:
                browser = await playwright.chromium.launch(
                    headless=self.headless,
                    args=self.browser_args
                )

                context = await browser.new_context()
                page = await context.new_page()

            await self.browser_pool.put((browser, context, page))

        logger.debug(f"Browser pool initialized with {self.browser_pool.qsize()} browsers")


    async def _solve_turnstile(self, task_id: str, url: str, sitekey: str, action: str = None, cdata: str = None):
        """Solve the Turnstile challenge."""

        browser, context, page = await self.browser_pool.get()
        start_time = time.time()

        try:
            if self.debug:
                logger.debug(f"Starting Turnstile solve for URL: {url}")
                logger.debug("Setting up page data and route")

            url_with_slash = url + "/" if not url.endswith("/") else url
            turnstile_div = f'<div class="cf-turnstile" data-sitekey="{sitekey}"' + (f' data-action="{action}"' if action else '') + (f' data-cdata="{cdata}"' if cdata else '') + '></div>'
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

                            logger.success(f"Successfully solved captcha: {value[:10]}... in {elapsed_time} Seconds")

                            self.results[task_id] = {"value": value, "elapsed_time": elapsed_time}
                            self._save_results()
                        break
                except:
                    pass

            if self.results.get(task_id) == "CAPCHA_NOT_READY":
                elapsed_time = round(time.time() - start_time, 3)
                self.results[task_id] = {"value": "CAPTCHA_FAIL", "elapsed_time": elapsed_time}

        except Exception as e:
            elapsed_time = round(time.time() - start_time, 3)
            self.results[task_id] = {"value": "CAPTCHA_FAIL", "elapsed_time": elapsed_time}
            logger.error(f"Error solving Turnstile: {str(e)}")
        finally:
            if self.debug:
                logger.debug("Clearing page state")
            await page.goto("about:blank")
            await self.browser_pool.put((browser, context, page))

    async def process_turnstile(self):
        """Handle the /turnstile endpoint requests."""
        url = request.args.get('url')
        sitekey = request.args.get('sitekey')
        action = request.args.get('action')
        cdata = request.args.get('cdata')

        if not url or not sitekey:
            logger.warning("Missing required parameters: 'url' or 'sitekey'")
            return jsonify({
                "status": "error",
                "error": "Both 'url' and 'sitekey' are required"
            }), 400

        if self.debug:
            logger.debug(f"Processing request for URL: {url}")
        task_id = str(uuid.uuid4())
        self.results[task_id] = "CAPTCHA_NOT_READY"

        try:
            asyncio.create_task(self._solve_turnstile(task_id=task_id, url=url, sitekey=sitekey, action=action, cdata=cdata))

            if self.debug:
                logger.debug(f"Request completed.")
            return jsonify({"task_id": task_id}), 202
        except Exception as e:
            logger.error(f"Unexpected error processing request: {str(e)}")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500

    async def get_result(self):
        """Return solved data"""
        task_id = request.args.get('id')

        if not task_id or task_id not in self.results:
            return jsonify({"status": "error", "error": "Invalid task ID/Request parameter"}), 400

        result = self.results[task_id]
        status_code = 200

        if "CAPTCHA_FAIL" in result:
            status_code = 422

        return result, status_code

    @staticmethod
    async def index():
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

    parser.add_argument('--headless', type=bool, default=False, help='Run the browser in headless mode, without opening a graphical interface. This option requires the --useragent argument to be set (default: False)')
    parser.add_argument('--useragent', type=str, default=None, help='Specify a custom User-Agent string for the browser. If not provided, the default User-Agent is used')
    parser.add_argument('--debug', type=bool, default=False, help='Enable or disable debug mode for additional logging and troubleshooting information (default: False)')
    parser.add_argument('--persistent', type=bool, default=False, help='Enable persistent context browser for better session handling and improved security (default: False)')
    parser.add_argument('--thread', type=int, default=1, help='Set the number of browser threads to use for multi-threaded mode. Increasing this will speed up execution but requires more resources (default: 1)')

    parser.add_argument('--host', type=str, default='127.0.0.1', help='Specify the IP address where the API solver runs. (Default: 127.0.0.1)')
    parser.add_argument('--port', type=str, default='5000', help='Set the port for the API solver to listen on. (Default: 5000)')
    return parser.parse_args()


def create_app(headless: bool, useragent: str, debug: bool, persistent: bool, thread: int) -> Quart:
    server = TurnstileAPIServer(headless=headless, useragent=useragent, debug=debug, persistent=persistent, thread=thread)
    return server.app


if __name__ == '__main__':
    args = parse_args()

    if args.headless is True and args.useragent is None:
        logger.error('You must specify a useragent for Turnstile Solver')
    else:
        app = create_app(headless=args.headless, useragent=args.useragent, debug=args.debug, persistent=args.persistent, thread=args.thread)
        app.run(host=args.host, port=int(args.port))

# Credits for the changes: github.com/sexfrance
# Credit for the original script: github.com/Theyka
