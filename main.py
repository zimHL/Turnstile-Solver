from undetected_playwright.sync_api import sync_playwright
import time


def main(playwright, headless=False, url=None, sitekey=None):
    args = ["--disable-blink-features=AutomationControlled"]

    browser = playwright.chromium.launch(
        headless=headless,
        args=args
    )

    url = url + "/" if not url.endswith("/") else url

    context = browser.new_context()
    page = context.new_page()

    with open("page.html") as f:
        page_data = f.read()
    stub = f"<div class=\"cf-turnstile\" data-sitekey=\"{sitekey}\"></div>"
    page_data = page_data.replace("<!-- cf turnstile -->", stub)


    page.route(url, lambda route: route.fulfill(body=page_data, status=200))
    page.goto(url)

    page.window_width = page.evaluate("window.innerWidth")
    page.window_height = page.evaluate("window.innerHeight")

    while True:
        turnstile_check = page.input_value("[name=cf-turnstile-response]")

        if turnstile_check == "":
            page.eval_on_selector("//div[@class='cf-turnstile']", "el => el.style.width = '70px'")
            page.click("//div[@class='cf-turnstile']")
            time.sleep(2)
        else:
            turnstile_value = page.query_selector("[name=cf-turnstile-response]").get_attribute("value")
            break

    context.close()
    browser.close()

    return turnstile_value


with sync_playwright() as ply:
    result = main(playwright=ply, headless=False, url="", sitekey="")
    print(result)
