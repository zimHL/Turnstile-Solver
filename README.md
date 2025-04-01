<div align="center">
 
  <h2 align="center">Cloudflare - Turnstile Solver</h2>
  <p align="center">
A Python-based Turnstile solver using the patchright library, featuring multi-threaded execution, API integration, and support for different browsers. It solves CAPTCHAs quickly and efficiently, with customizable configurations and detailed logging.
    <br />
    <br />
    <a href="https://github.com/Theyka/Turnstile-Solver#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">💡 Request Feature</a>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/LICENSE-CC%20BY%20NC%204.0-red?style=for-the-badge"/>
    <img src="https://img.shields.io/github/stars/Theyka/Turnstile-Solver.svg?style=for-the-badge&color=red"/>
    <img src="https://img.shields.io/github/issues/Theyka/Turnstile-Solver?style=for-the-badge&color=red"/>
  </p>
</div>

---

### 🎁 Donation

- **USDT (TRC20)**: ``TWXNQCnJESt6gxNMX5oHKwQzq4gsbdLNRh``
- **USDT (Arbitrum One)**: ``0xd8fd1e91c8af318a74a0810505f60ccca4ca0f8c``
- **BTC**:
``1AbiR2YaCzvmy9itMAJqHejYYENtogDr78``
- **LTC**: ``LSrLQe2dfpDhGgVvDTRwW72fSyC9VsXp9g``

---

### ⚙️ Installation Instructions

1. **Ensure Python 3.8+ is installed** on your system.

2. **Create a Python virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Select the browser to install**:
   You can choose between **Chromium**, **Chrome**, **Edge** or **Camoufox**:
   - To install **Chromium**:
     ```bash
     python -m patchright install chromium
     ```
   - To install **Chrome**:
     - On **macOS/Windows**: [Click here](https://www.google.com/chrome/)  
     - On **Linux (Debian/Ubuntu-based)**:
       ```bash
       apt update
       wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
       apt install -y ./google-chrome-stable_current_amd64.deb
       apt -f install -y  # Fix dependencies if needed
       rm ./google-chrome-stable_current_amd64.deb
       ```
   - To install **Edge**:
     ```bash
     python -m patchright install msedge
     ```
   - To install **Camoufox**:
     ```bash
     python -m camoufox fetch
     ```

6. **Start testing**:
   - Run the script (Check [🔧 Command line arguments](#-command-line-arguments) for better setup):
     ```bash
     python api_solver.py
     ```

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
| `--useragent`  | `None`   | `string`  | Specifies a custom User-Agent string for the browser. (No need to set if camoufox used)                                        |
| `--debug`      | `False`  | `boolean` | Enables or disables debug mode for additional logging and troubleshooting.                   |
| `--browser_type` | `chromium`  | `string` | Specify the browser type for the solver. Supported options: chromium, chrome, msedge, camoufox      |
| `--thread`     | `1`      | `integer` | Sets the number of browser threads to use in multi-threaded mode.                           |
| `--host`       | `127.0.0.1` | `string`  | Specifies the IP address the API solver runs on.                                            |
| `--port`       | `5000`   | `integer` | Sets the port the API solver listens on.                                                    |
| `--proxy`       | `False`   | `boolean` | Select a random proxy from proxies.txt for solving captchas                                                   |

---

### 🐳 Docker Image
#### Running the Container
To start the container, use:
- Change the TZ environment variable and ports to the correct one for yourself:
```sh
docker run -d -p 3389:3389 -p 5000:5000 -e TZ=Asia/Baku --name turnstile_solver theyka/turnstile_solver:latest
```

#### Connecting to the Container
1. Use an **RDP client** (like Windows Remote Desktop, Remmina, or FreeRDP)
2. Connect to `localhost:3389`
3. Login with the default user:
   - **Username:** root
   - **Password:** root
4. After this, you can start the solver by navigating to the `Turnstile-Solver` folder.

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

### 📝 TODO List  
- [x] Add `cData` and `Action` support  
- [x] Add multi-threaded solving method
- [x] Add Docker support  
- [x] Fix headless mode  
- [x] Update [`main.py`](https://github.com/Theyka/Turnstile-Solver/blob/main/main.py), [`async_solver.py`](https://github.com/Theyka/Turnstile-Solver/blob/main/async_solver.py), and [`sync_solver.py`](https://github.com/Theyka/Turnstile-Solver/blob/main/sync_solver.py) 
- [x] Add proxy support  

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

v0.2.0 ⋮ 24/02/2025  
+ Added Camoufox support

v0.2.1 ⋮ 24/02/2025  
+ Fixed main.py, async_solver.py and sync_solver.py

v0.2.2 ⋮ 24/02/2025  
+ Added proxy support

v0.2.4 ⋮ 01/03/2025  
+ Added edge support
```

---

Inspired by [Turnaround](https://github.com/Body-Alhoha/turnaround)
Original code by [Theyka](https://github.com/Theyka/Turnstile-Solver)
Changes by [Sexfrance](https://github.com/sexfrance)
