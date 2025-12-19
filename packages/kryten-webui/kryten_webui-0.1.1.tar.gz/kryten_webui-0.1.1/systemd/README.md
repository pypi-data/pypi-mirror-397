# Systemd Service Files

This directory contains systemd service unit files for running kryten-webui as a system service.

## Installation

1. Copy the service file to systemd directory:
```bash
sudo cp systemd/kryten-webui.service /etc/systemd/system/
```

2. Reload systemd daemon:
```bash
sudo systemctl daemon-reload
```

3. Enable the service to start on boot:
```bash
sudo systemctl enable kryten-webui
```

4. Start the service:
```bash
sudo systemctl start kryten-webui
```

## Service Management

Check service status:
```bash
sudo systemctl status kryten-webui
```

View logs:
```bash
sudo journalctl -u kryten-webui -f
```

Stop the service:
```bash
sudo systemctl stop kryten-webui
```

Restart the service:
```bash
sudo systemctl restart kryten-webui
```

## Configuration

The service expects:
- Installation directory: `/opt/kryten-webui`
- Configuration file: `/etc/kryten/webui/config.json`
- User/Group: `kryten`
- Log directory: `/var/log/kryten-webui`

Make sure to create these directories and the kryten user before starting the service.
