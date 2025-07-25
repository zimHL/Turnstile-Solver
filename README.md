<div align="center">
 
  <h2 align="center">Cloudflare - Turnstile Solver</h2>
  <p align="center">
一个基于 Python 和 Patchright 库的 Turnstile 解决方案，具有多线程执行、API 集成和多浏览器支持的特点。它能高效快速地解决 CAPTCHA，并提供可定制的配置和详细的日志记录。
    <br />
    <br />
    <a href="https://github.com/Theyka/Turnstile-Solver#-changelog">📜 更新日志</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">⚠️ 报告问题</a>
    ·
    <a href="https://github.com/Theyka/Turnstile-Solver/issues">💡 功能建议</a>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/LICENSE-CC%20BY%20NC%204.0-red?style=for-the-badge"/>
    <img src="https://img.shields.io/github/stars/Theyka/Turnstile-Solver.svg?style=for-the-badge&color=red"/>
    <img src="https://img.shields.io/github/issues/Theyka/Turnstile-Solver?style=for-the-badge&color=red"/>
    <a href="https://t.me/codarea">
     <img src="https://img.shields.io/badge/Telegram%20Channel-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
    </a>
  </p>
</div>

---

### 🎁 捐赠

- **USDT (TRC20)**: `TWXNQCnJESt6gxNMX5oHKwQzq4gsbdLNRh`
- **USDT (Arbitrum One)**: `0xd8fd1e91c8af318a74a0810505f60ccca4ca0f8c`
- **BTC**: `1AbiR2YaCzvmy9itMAJqHejYYENtogDr78`
- **LTC**: `LSrLQe2dfpDhGgVvDTRwW72fSyC9VsXp9g`

---

### ❓ 需要定制解决方案？
- 需要如 Cloudflare Interstitial 等定制化解决方案？请通过 Telegram 联系我:

  <a href="https://t.me/tlb_sh">
    <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
  </a>

---

### ❗ 免责声明
- 我不对任何可能发生的事情负责，例如 API 封锁、IP 被禁等。
- 这是一个为了娱乐和个人使用而快速制作的项目。如果您希望看到更多更新，请给本仓库点赞（Star）并通过 [这里](https://github.com/Theyka/Turnstile-Solver/issues/) 提交 "issue"。

---

### 🐳 使用 Docker Compose 部署 (推荐)

此方法是为服务器部署设计的**最佳实践**。它使用 `camoufox` 浏览器，镜像体积小，无需图形界面，并且易于管理和配置。

#### **先决条件**
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### **步骤 1: 获取项目文件**
首先，将项目克隆到您的服务器上。
```bash
git clone https://github.com/Theyka/Turnstile-Solver.git
cd Turnstile-Solver
```

#### **步骤 2: 配置 `docker-compose.yml`**
在项目根目录下创建一个 `docker-compose.yml` 文件，内容如下。您可以根据需要修改端口映射和环境变量。

```yaml
version: '3.8'

services:
  turnstile_solver:
    # 如果您想自己构建镜像，请取消下面的注释
    # build: .
    # 如果您想使用预构建的镜像，请使用下面这行
    image: zim/turnstile_solver:latest # 假设您已经构建或拉取了此镜像
    container_name: turnstile_solver
    ports:
      - "59031:5000" # 左侧是您服务器的端口，右侧是容器内的端口
    volumes:
      # 将本地的 camoufox_cache 目录挂载到容器内，用于持久化存储浏览器文件
      - ./camoufox_cache:/root/.cache
    environment:
      # [必需] 设置为 true 以启动 API 服务
      - RUN_API_SOLVER=true
      # [必需] 浏览器类型，推荐使用 camoufox
      - BROWSER_TYPE=camoufox
      # [必需] 时区设置
      - TZ=Asia/Shanghai
      # --- 以下为可选参数，对应命令行参数 ---
      - THREAD=2           # 设置线程数 (例如: 2)
      - HOST=0.0.0.0       # 容器内监听的地址，保持 0.0.0.0 即可
      - PORT=5000          # 容器内监听的端口
      # - HEADLESS=true      # 如需开启无头模式，请取消注释
      # - USERAGENT="Your Custom User Agent" # 无头模式下建议设置
      # - DEBUG=true         # 如需开启调试模式，请取消注释
    restart: unless-stopped
```

#### **步骤 3: 首次初始化 (下载浏览器)**
在首次启动服务前，您需要下载 `camoufox` 浏览器文件。我们提供了自动化脚本来完成此操作。

- **在 Windows 上:**
  双击运行 `init.cmd` 脚本。

- **在 Linux / macOS 上:**
  在终端中运行 `init.sh` 脚本 (可能需要先授予执行权限: `chmod +x init.sh`)。
  ```bash
  ./init.sh
  ```
**注意:** 此过程将下载数百MB的文件，请耐心等待。此步骤只需执行一次。

#### **步骤 4: 启动服务**
初始化完成后，使用以下命令在后台启动服务：
```bash
docker compose up -d
```

#### **日常管理**
- **查看日志:** `docker compose logs`
- **停止服务:** `docker compose down`

---

### ⚙️ 手动安装说明 (适合本地开发)

1.  **确保已安装 Python 3.8+**。
2.  **创建 Python 虚拟环境**: `python -m venv venv`
3.  **激活虚拟环境**:
    - **Windows**: `venv\Scripts\activate`
    - **macOS/Linux**: `source venv/bin/activate`
4.  **安装依赖**: `pip install -r requirements.txt`
5.  **安装浏览器**:
    选择 **Chromium**, **Chrome**, **Edge** 或 **Camoufox** 中的一个：
    - **Camoufox (推荐)**: `python -m camoufox fetch`
    - **Chromium**: `python -m patchright install chromium`
    - **Edge**: `python -m patchright install msedge`
    - **Chrome**: 请参考官方文档进行安装。
6.  **启动测试**: `python api_solver.py` (更多参数见下方)

---

### 🔧 命令行参数
| 参数 | 默认值 | 类型 | 描述 |
|---|---|---|---|
| `--headless` | `False` | `boolean` | 以无头模式运行浏览器。 |
| `--useragent` | `None` | `string` | 指定自定义 User-Agent。 |
| `--debug` | `False` | `boolean` | 启用调试模式以获取更多日志。 |
| `--browser_type` | `chromium` | `string` | 指定浏览器类型: `chromium`, `chrome`, `msedge`, `camoufox`。 |
| `--thread` | `1` | `integer` | 设置多线程模式下的浏览器线程数。 |
| `--host` | `127.0.0.1` | `string` | API 服务监听的 IP 地址。 |
| `--port` | `5000` | `integer` | API 服务监听的端口。 |
| `--proxy` | `False` | `boolean` | 从 `proxies.txt` 中随机选择代理。 |

---

### 🐳 旧版Docker部署 (带远程桌面)
此方法提供一个包含完整桌面环境的镜像，您可以通过 RDP 客户端连接进去手动操作。

#### **运行容器**
- 请根据需要修改 `TZ` 环境变量和端口映射：
```sh
docker run -d -p 3389:3389 -p 5000:5000 -e TZ=Asia/Baku --name turnstile_solver theyka/turnstile_solver:latest
```

#### **连接到容器**
1.  使用 **RDP 客户端** (如 Windows 远程桌面)。
2.  连接到 `localhost:3389`。
3.  使用默认凭据登录:
    - **用户名:** root
    - **密码:** root
4.  登录后，进入 `Turnstile-Solver` 文件夹即可启动求解器。

---

### 📡 API 文档
#### 提交 Turnstile 任务
```http
  GET /turnstile?url=https://example.com&sitekey=0x4AAAAAAA
```
| 参数 | 类型 | 描述 | 必填 |
|---|---|---|---|
| `url` | string | 包含验证码的目标 URL。 | 是 |
| `sitekey` | string | 需要解决的验证码的 Site Key。 | 是 |
| `action` | string | 解决验证码时触发的动作，例如 `login`。 | 否 |
| `cdata` | string | 可用于附加验证码参数的自定义数据。 | 否 |

**响应:**
```json
{
  "task_id": "d2cbb257-9c37-4f9c-9bc7-1eaee72d96a8"
}
```

#### 获取结果
```http
  GET /result?id=f0dbe75b-fa76-41ad-89aa-4d3a392040af
```
| 参数 | 类型 | 描述 | 必填 |
|---|---|---|---|
| `id` | string | 从 `/turnstile` 请求返回的唯一任务 ID。 | 是 |

**响应:**
```json
{
  "elapsed_time": 7.625,
  "value": "0.KBtT-r"
}
```

---

### 🎉 赞助商
<a href="https://dashboard.capsolver.com/passport/register?inviteCode=7_Dvkat0RVqc">
    <img src="https://github.com/user-attachments/assets/176d2a43-2d08-4aa6-bc9d-5e1eb5c3d1a4" alt="Description">
</a>

---

Inspired by [Turnaround](https://github.com/Body-Alhoha/turnaround)
Original code by [Theyka](https://github.com/Theyka/Turnstile-Solver)
Changes by [Sexfrance](https://github.com/sexfrance)
