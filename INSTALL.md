# INSTALL.md

## JioPC Automated Testing Agent

### System Requirements

* Ubuntu 24.04 LTS
* Python 3.12+
* Internet connectivity (required for website testing and LLM analysis)
* Minimum:

  * 4 vCPU
  * 8 GB RAM

---

# Option 1: Run from Source

## 1. Clone Repository

```bash
git clone <repository-url>
cd jiopc-agent
```

## 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Install Playwright Browser

```bash
playwright install chromium
```

## 5. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LLM_API_KEY=<your-api-key>

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-email>
SMTP_PASSWORD=<gmail-app-password>
```

SMTP settings are optional and only required for email delivery.

## 6. Run the Agent

Run the complete test suite:

```bash
python jiopc_agent.py --config jiopc-agent.yaml
```

Run a single component:

```bash
python jiopc_agent.py --config jiopc-agent.yaml --part A
python jiopc_agent.py --config jiopc-agent.yaml --part B
python jiopc_agent.py --config jiopc-agent.yaml --part C
```

Run tests and LLM analysis:

```bash
python jiopc_agent.py --config jiopc-agent.yaml --analyse
```

Run standalone analysis on an existing log:

```bash
python analyse.py \
    --log ~/.local/share/jiopc/agent/test_run_<timestamp>.log
```

---

# Option 2: Install Debian Package

## 1. Install Package (available in packaging/ in repo)

```bash
sudo apt install ./jiopc-agent_1.0_all.deb
```

The package installs the agent under:

```text
/opt/jiopc-agent/
```

and creates the launcher:

```text
/usr/local/bin/jiopc-agent
```

## 2. Configure Environment Variables

Create:

```bash
sudo nano /opt/jiopc-agent/.env
```

Example:

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LLM_API_KEY=<your-api-key>

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-email>
SMTP_PASSWORD=<gmail-app-password>
```

## 3. Run the Agent

Using default packaged configuration:

```bash
jiopc-agent
```

Run with analysis:

```bash
jiopc-agent --analyse
```

Run a specific component:

```bash
jiopc-agent --part A
jiopc-agent --part B
jiopc-agent --part C
```

Run with a custom YAML file (following the format specified in DESIGN.md):

```bash
jiopc-agent --config my-config.yaml
```

---

# Output Files

Logs are written to:

```text
~/.local/share/jiopc/agent/
```

Generated files include:

```text
test_run_<timestamp>.log
test_run_<timestamp>.analysis.txt
```

---

# Troubleshooting

### Playwright Browser Missing

```bash
playwright install chromium
```

### SMTP Email Not Sending

Verify:

* SMTP server
* SMTP port
* Username
* App password
* Network access to the SMTP endpoint

### LLM Analysis Fails

Verify:

```env
LLM_BASE_URL
LLM_MODEL
LLM_API_KEY
```

are correctly configured.

---

# Uninstall

```bash
sudo apt remove jiopc-agent
```

Optional cleanup:

```bash
sudo rm -rf /opt/jiopc-agent
rm -rf ~/.local/share/jiopc/agent
```
