# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- NATS server (running and accessible)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/grobertson/kryten-webui.git
cd kryten-webui
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Configure the Service

Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit `config.json` with your settings:

```json
{
  "nats_url": "nats://localhost:4222",
  "nats_subject_prefix": "cytube",
  "service_name": "kryten-webui"
}
```

### 4. Run the Service

**Development mode:**

```bash
poetry run kryten-webui --config config.json --log-level DEBUG
```

**Using startup script (PowerShell):**

```powershell
.\start-webui.ps1
```

**Using startup script (Bash):**

```bash
./start-webui.sh
```

## Production Installation

### System User Setup

Create a dedicated system user:

```bash
sudo useradd -r -s /bin/false -d /opt/kryten-webui kryten
```

### Installation Directory

```bash
sudo mkdir -p /opt/kryten-webui
sudo chown kryten:kryten /opt/kryten-webui
```

### Configuration Directory

```bash
sudo mkdir -p /etc/kryten/webui
sudo chown kryten:kryten /etc/kryten/webui
sudo cp config.example.json /etc/kryten/webui/config.json
sudo chown kryten:kryten /etc/kryten/webui/config.json
sudo chmod 600 /etc/kryten/webui/config.json
```

Edit the configuration:

```bash
sudo nano /etc/kryten/webui/config.json
```

### Log Directory

```bash
sudo mkdir -p /var/log/kryten-webui
sudo chown kryten:kryten /var/log/kryten-webui
```

### Install Application

```bash
cd /opt/kryten-webui
sudo -u kryten git clone https://github.com/grobertson/kryten-webui.git .
sudo -u kryten poetry install --no-dev
```

### Systemd Service

Install the systemd service:

```bash
sudo cp systemd/kryten-webui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kryten-webui
sudo systemctl start kryten-webui
```

Check service status:

```bash
sudo systemctl status kryten-webui
sudo journalctl -u kryten-webui -f
```

## Updating

### Development

```bash
git pull
poetry install
```

### Production

```bash
cd /opt/kryten-webui
sudo systemctl stop kryten-webui
sudo -u kryten git pull
sudo -u kryten poetry install --no-dev
sudo systemctl start kryten-webui
```

## Troubleshooting

### Check NATS Connection

Ensure NATS server is running:

```bash
# Check if NATS is listening
netstat -tuln | grep 4222
```

### View Logs

```bash
# Systemd service logs
sudo journalctl -u kryten-webui -f

# Check for errors
sudo journalctl -u kryten-webui --since "1 hour ago" | grep -i error
```

### Test Configuration

```bash
# Validate JSON syntax
python -m json.tool config.json

# Test connection manually
poetry run kryten-webui --config config.json --log-level DEBUG
```

### Permissions Issues

Ensure correct ownership:

```bash
sudo chown -R kryten:kryten /opt/kryten-webui
sudo chown -R kryten:kryten /etc/kryten/webui
sudo chown -R kryten:kryten /var/log/kryten-webui
```

## Uninstalling

### Stop and Disable Service

```bash
sudo systemctl stop kryten-webui
sudo systemctl disable kryten-webui
sudo rm /etc/systemd/system/kryten-webui.service
sudo systemctl daemon-reload
```

### Remove Files

```bash
sudo rm -rf /opt/kryten-webui
sudo rm -rf /etc/kryten/webui
sudo rm -rf /var/log/kryten-webui
```

### Remove User

```bash
sudo userdel kryten
```
