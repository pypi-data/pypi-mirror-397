# 🧩 OPM — Odoo Plugin Manager (CLI)

**OPM** is a modern and lightweight command-line tool for Odoo developers.  
It automates **cache refresh**, **hot reload**, **quick module upgrades**, and **test execution** — all without restarting Odoo.

Compatible with **Odoo 15 → 18**, supporting both **Docker** and **bare-metal** environments.

---

## ⚙️ Installation

Install from PyPI:

```bash
pip install odoo-plugin-manager
```

Or update to the latest version:

```bash
pip install -U odoo-plugin-manager
```

---

## 📁 Configuration (`opm.yaml`)

When you first run any OPM command, it automatically creates an `opm.yaml` file in your working directory.  
This file defines your Odoo connection details and runtime environment.

### Example configuration

```yaml
runtime:
  odoo_url: "http://localhost:10017"
  db: "main"
  user: "admin"
  pass: "admin"
  addons:
    - "/path/to/your/addons"
  container: "odoo18"   # Docker container name OR "" if running on host
  ws_host: "127.0.0.1"
  ws_port: 8765
```

> **Container rule:**
> - For Docker: set `container: "your-container-name"`
> - For bare-metal: set `container: ""`

---

## 🚀 Core Commands

### 🪄 `opm init`

Creates a new `opm.yaml` configuration file interactively.

```bash
opm init
```

Example output:

```
[opm] Creating opm.yaml configuration...
[opm] ✅ Configuration created successfully at ./opm.yaml
```

---

### ⚙️ `opm dev`

Starts **development mode** — a live-reload watcher that detects file changes and automatically refreshes your browser or flushes Odoo caches.

```bash
opm dev
```

#### 🔁 What happens under the hood:
- Watches your addon folders (`addons/`) for file changes  
- When `.xml`, `.js`, or `.scss` files change → triggers a **cache flush**  
- When `.py` or `__manifest__.py` changes → triggers a **quick module upgrade**  
- Notifies all connected browsers via **WebSocket** to auto-reload the page  

#### 💡 Keyboard Shortcuts
While `opm dev` is running in your terminal:
- Press **`r`** → manually trigger a browser reload  
- Press **`Ctrl+C`** → safely stop the development server  

#### 🌐 WebSocket Setup
When `opm dev` runs, it opens a WebSocket server (default: `ws://127.0.0.1:8765`).  
Your Odoo frontend connects to this server to receive reload notifications.

If Odoo is hosted behind **Nginx**, configure it like this:

```nginx
location /__opm__/ws {
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_pass http://127.0.0.1:8765;
}
```

#### 🔒 Notes
- If running on localhost, the WebSocket connects directly.
- On production/staging behind Nginx, it connects via `/__opm__/ws`.

---

### 🧩 `opm update <module>`

Updates (or installs) a single module — automatically flushes caches and triggers live reload if `opm dev` is running.

```bash
opm update my_module
```

#### What it does:
1. Detects Odoo binary automatically (works in Docker or locally)  
2. Runs `-i` and `-u` flags for your module  
3. Flushes Odoo caches via RPC after success  
4. If `opm dev` is active → triggers browser reload automatically  

Example output:
```
[opm] 🧪 Starting update run…
[opm] ▶️  Executing update command…
✅ Update finished successfully.
[opm] Post-update: caches flushed via RPC.
```

---

### 🧪 `opm test <module>`

Runs tests for the specified Odoo module.  
If the module is not yet installed, OPM installs or upgrades it before testing.

```bash
opm test my_module
```

Example output:
```
[opm] Odoo binary detected: /usr/bin/odoo
[opm] Running tests for module: my_module
✅ Tests finished successfully.
```

Failed tests:
```
❌ Tests failed. See .opm/artifacts/test_last.log for details.
```

All test logs are automatically saved in:

```
.opm/artifacts/
```

---

### 🩺 `opm diagnose`

Runs a diagnostic check to ensure Odoo and OPM configuration are correct.

```bash
opm diagnose
```

Example output:

```
[opm] 🔍 Running environment diagnostics...
[opm] Docker CLI: ✅ Found
[opm] Odoo binary: ✅ Found (/usr/bin/odoo)
[opm] Testing Odoo URL: http://localhost:10017
[opm] ✅ Odoo instance reachable.
[opm] 🏁 Diagnose complete.
```

---

## 🧠 Features

| Feature                        | Description                                                         |
| ------------------------------ | ------------------------------------------------------------------- |
| ⚙️ **Automatic Cache Refresh** | Detects XML, QWeb, or JS changes and flushes Odoo caches instantly. |
| 🧪 **Module Install/Upgrade**  | Automatically installs or upgrades modules before running tests.    |
| 🗱 **Docker Integration**      | Detects and executes inside Odoo containers automatically.          |
| 📦 **Artifact Logging**        | Saves logs and test outputs under `.opm/artifacts/`.                |
| ⚡ **YAML Config System**       | Uses a single `opm.yaml` file for all environment details.          |
| 🧠 **RPC-Based Architecture**  | Works with Odoo via XML-RPC — no code injection or patching needed. |

---

## 🔮 Future Roadmap

These are upcoming features currently under development:

* 🔁 **Hot Reload** — true live reload support for Odoo front-end assets
* 🧩 **Advanced Helper Addon (`opm_dev_helper`)** — deeper cache and UI refresh controls
* 📊 **Improved Test Reporting** — detailed test result summaries and coverage integration

---

## 🧠 Technical Overview

| Key                    | Details                                             |
| ---------------------- | --------------------------------------------------- |
| **Language**           | Python 3.10+                                        |
| **Dependencies**       | typer, rich, watchdog, requests, pyyaml, websockets |
| **Odoo Compatibility** | 15 → 18                                             |
| **Platforms**          | macOS / Linux                                       |
| **Configuration File** | `opm.yaml` (auto-created on first run)              |

---

## 🦦 Example Workflow

A simple developer workflow might look like this:

```bash
# 1️⃣ Initialize config
opm init

# 2️⃣ Check your setup
opm diagnose

# 3️⃣ Start development mode (watch for file changes)
opm dev

# 4️⃣ Run tests for your module
opm test my_module

# 5️⃣ Update your module and auto-reload browser
opm update my_module
```

This setup keeps your Odoo instance responsive
and your local development cycle short — no manual restarts needed.

---

## 📜 License

Licensed under the **GNU General Public License v3 (GPL-3.0-or-later)**.  
The OPM CLI is open source.  
Future Odoo-specific helper addons may be released under a separate commercial license.

---

© 2025 Ahmet Atakan — Crafted for real Odoo developers who build faster, smarter, and cleaner.
