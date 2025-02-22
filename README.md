<div align="center">
 
  <h2 align="center">Cloudflare - Turnstile Solver</h2>
  <p align="center">
A Python-based solution for solving Cloudflare Turnstile challenges quickly (4-6 seconds solve time). The script uses patchright library to interact with web pages and solve the challenges without running additional browser instances.
    <br />
    <br />
    <a href="https://github.com/Theyka/Turnstile-Solver#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation
- Requires: `Python 3.8+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`
- Install chromium: `patchright install chromium` / `python -m patchright install chromium`
- Start: `Remove comments for testing in async and sync python files then run those`

---

### 🔥 Features
- **Debug Logging**: Detailed debug logs track actions and progress, making troubleshooting straightforward.
- **Automated CAPTCHA Solver**: Uses Playwright to launch a browser, navigate to the target page, and dynamically injects a CAPTCHA solver.
- **Multi-threaded Mode**: Supports multi-threaded execution, allowing multiple browser instances to run concurrently, speeding up processing.
- **Persistent Browser Context**: Uses a persistent context browser for better security and session management across multiple runs.
- **API Server Integration**: Implements an API server for easy integration, offering customizable configurations like host and port, and exposing essential functions.
- **Customizable Browser Context**: Sets browser options like headless mode, sandboxing, and disabling unnecessary features to optimize performance.
- **Responsive CAPTCHA Interaction**: Adjusts CAPTCHA display, clicks on it, and retrieves the response through repeated attempts if necessary.
- **Timeout and Retries**: Implements a retry loop with configurable timeouts, ensuring robust attempts to retrieve the CAPTCHA token.
- **Elapsed Time Tracking**: Logs and returns elapsed time for solving CAPTCHA, providing an efficiency metric.
- **Error Handling**: Returns detailed status messages on success or failure, allowing for straightforward integration and feedback.

---

### ❗ Disclaimers
- I am not responsible for anything that may happen, such as API Blocking, IP ban, etc.
- This was a quick project that was made for fun and personal use if you want to see further updates, star the repo & create an "issue" [here](https://github.com/Theyka/Turnstile-Solver/issues/)

---

### 🔧 Command line arguments
| Parameter     | Default   | Type      | Description                                                                                   |
|--------------|-----------|-----------|-----------------------------------------------------------------------------------------------|
| `--headless`   | `False`  | `boolean` | Runs the browser in headless mode. Requires the `--useragent` argument to be set.             |
| `--useragent`  | `None`   | `string`  | Specifies a custom User-Agent string for the browser.                                        |
| `--debug`      | `False`  | `boolean` | Enables or disables debug mode for additional logging and troubleshooting.                   |
| `--persistent` | `False`  | `boolean` | Enables a persistent browser context for better session handling and improved security.      |
| `--thread`     | `1`      | `integer` | Sets the number of browser threads to use in multi-threaded mode.                           |
| `--host`       | `127.0.0.1` | `string`  | Specifies the IP address the API solver runs on.                                            |
| `--port`       | `5000`   | `integer` | Sets the port the API solver listens on.                                                    |

---

### 📡 API Documentation
#### Solve turnstile
```http
  GET /turnstile?url=https://example.com&sitekey=0x4AAAAAAA
```
#### Request Parameters:
| Parameter  | Type    | Description                                                                 | Required |
|------------|---------|-----------------------------------------------------------------------------|----------|
| `url`      | string  | The target URL containing the CAPTCHA. (e.g., `https://example.com`) | Yes      |
| `sitekey`  | string  | The site key for the CAPTCHA to be solved. (e.g., `0x4AAAAAAA`) | Yes      |
| `action`   | string  | Action to trigger during CAPTCHA solving, e.g., `login`            | No       |
| `cdata`    | string  | Custom data that can be used for additional CAPTCHA parameters.    | No       |

#### Response:

If the request is successfully received, the server will respond with a `task_id` for the CAPTCHA solving task:

```json
{
  "task_id": "d2cbb257-9c37-4f9c-9bc7-1eaee72d96a8"
}
```

#### Get Result
```http
  GET /result?id=f0dbe75b-fa76-41ad-89aa-4d3a392040af
```

#### Request Parameters:

| Parameter  | Type    | Description                                                                 | Required |
|------------|---------|-----------------------------------------------------------------------------|----------|
| `id`       | string  | The unique task ID returned from the `/turnstile` request.                   | Yes      |

#### Response:

If the CAPTCHA is solved successfully, the server will respond with the following information:

```json
{
  "elapsed_time": 7.625,
  "value": "0.KBtT-r"
}
```

---

### 📜 ChangeLog
```diff
v0.0.1 ⋮ 21/10/2024
! Initial release

v0.0.2 ⋮ 28/10/2024
! Modified the script, page.html is now in the scripts
! Made it faster and less resource intensive
! Modified the sync logic and made an async version
! Implemented logmagix logging
! Added timer

v0.1.0 ⋮ 11/7/2024
+ Added API server implementation
+ Added web interface for API documentation
+ Improved error handling and logging
+ Added concurrent processing support

v0.1.1 ⋮ 15/2/2025
+ Added --headless argument
+ Added --debug argument
+ Added --useragent argument
! Modified logging method to use the logging library

v0.1.2 ⋮ 19/02/2025  
+ Added optional action and cData parameters, similar to sitekey and url.

v0.1.3 ⋮ 22/02/2025  
+ Added persistent context browser for improved security
+ Implemented multi-threaded mode for enhanced performance
+ Added method to configure host and port for API server
```

---

<p align="center">
  <img src="https://img.shields.io/github/license/Theyka/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/Theyka/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/Theyka/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>

Inspired by [Turnaround](https://github.com/Body-Alhoha/turnaround)
Original code by [Theyka](https://github.com/Theyka/Turnstile-Solver)
Changes by [Sexfrance](https://github.com/sexfrance)
