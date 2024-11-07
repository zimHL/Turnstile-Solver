from patchright.async_api import async_playwright
from quart import Quart, request, jsonify
import threading

app = Quart(__name__)

browser_lock = threading.Lock()


async def run_browser():
    global page
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ]
    )
    context = await browser.new_context()
    page = await context.new_page()


@app.before_serving
async def startup():
    await run_browser()


async def main(url=None, sitekey=None):
    url = url + "/" if not url.endswith("/") else url

    with open("page.html") as f:
        page_data = f.read()
    stub = f"<div class=\"cf-turnstile\" data-sitekey=\"{sitekey}\"></div>"
    page_data = page_data.replace("<!-- cf turnstile -->", stub)


    await page.route(url, lambda route: route.fulfill(body=page_data, status=200))


    await page.goto(url)

    await page.eval_on_selector("//div[@class='cf-turnstile']", "el => el.style.width = '70px'")

    while True:
        turnstile_check = await page.input_value("[name=cf-turnstile-response]")
        if turnstile_check == "":
            await page.click("//div[@class='cf-turnstile']")
        else:
            element = await page.query_selector("[name=cf-turnstile-response]")
            turnstile_value = await element.get_attribute("value") if element else None
            break

    result = {
        "result": turnstile_value
    }
    await page.goto("about:blank")

    return result


@app.route('/turnstile', methods=['GET'])
async def process_turnstile():
    url = request.args.get('url')
    sitekey = request.args.get('sitekey')

    if not url or not sitekey:
        return jsonify({"error": "Both 'url' and 'sitekey' are required"}), 400

    with browser_lock:
        try:
            turnstile_solver = await main(url=url, sitekey=sitekey)
            return jsonify(turnstile_solver), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/')
async def index():
    return """
    <h1>Welcome to Turnstile Solver API</h1>
    <p>To use the turnstile service, send a GET request to <code>/turnstile</code> with the following query parameters:</p>
    <p>This project is inspired by <a href="https://github.com/Body-Alhoha/turnaround">Turnaround</a> and is currently maintained by <a href="https://github.com/Theyka">Theyka</a>.</p>
    <ul>
        <li><strong>url</strong>: The URL where Turnstile is to be validated</li>
        <li><strong>sitekey</strong>: The site key for Turnstile</li>
    </ul>
    <p>Example usage: <code>/turnstile?url=https://example.com&sitekey=sitekey</code></p>
    """


if __name__ == '__main__':
    app.run()
