# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- NATS server (running and accessible)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/grobertson/kryten-bingo.git
cd kryten-bingo
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
  "service_name": "kryten-bingo"
}
```

### 4. Run the Service

**Development mode:**

```bash
poetry run kryten-bingo --config config.json --log-level DEBUG
```

**Using startup script (PowerShell):**

```powershell
.\start-bingo.ps1
```

**Using startup script (Bash):**

```bash
./start-bingo.sh
```

## Production Installation

### System User Setup

Create a dedicated system user:

```bash
sudo useradd -r -s /bin/false -d /opt/kryten-bingo kryten
```

### Installation Directory

```bash
sudo mkdir -p /opt/kryten-bingo
sudo chown kryten:kryten /opt/kryten-bingo
```

### Configuration Directory

```bash
sudo mkdir -p /etc/kryten/bingo
sudo chown kryten:kryten /etc/kryten/bingo
sudo cp config.example.json /etc/kryten/bingo/config.json
sudo chown kryten:kryten /etc/kryten/bingo/config.json
sudo chmod 600 /etc/kryten/bingo/config.json
```

Edit the configuration:

```bash
sudo nano /etc/kryten/bingo/config.json
```

### Log Directory

```bash
sudo mkdir -p /var/log/kryten-bingo
sudo chown kryten:kryten /var/log/kryten-bingo
```

### Install Application

```bash
cd /opt/kryten-bingo
sudo -u kryten git clone https://github.com/grobertson/kryten-bingo.git .
sudo -u kryten poetry install --no-dev
```

### Systemd Service

Install the systemd service:

```bash
sudo cp systemd/kryten-bingo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kryten-bingo
sudo systemctl start kryten-bingo
```

Check service status:

```bash
sudo systemctl status kryten-bingo
sudo journalctl -u kryten-bingo -f
```

## Updating

### Development

```bash
git pull
poetry install
```

### Production

```bash
cd /opt/kryten-bingo
sudo systemctl stop kryten-bingo
sudo -u kryten git pull
sudo -u kryten poetry install --no-dev
sudo systemctl start kryten-bingo
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
sudo journalctl -u kryten-bingo -f

# Check for errors
sudo journalctl -u kryten-bingo --since "1 hour ago" | grep -i error
```

### Test Configuration

```bash
# Validate JSON syntax
python -m json.tool config.json

# Test connection manually
poetry run kryten-bingo --config config.json --log-level DEBUG
```

### Permissions Issues

Ensure correct ownership:

```bash
sudo chown -R kryten:kryten /opt/kryten-bingo
sudo chown -R kryten:kryten /etc/kryten/bingo
sudo chown -R kryten:kryten /var/log/kryten-bingo
```

## Uninstalling

### Stop and Disable Service

```bash
sudo systemctl stop kryten-bingo
sudo systemctl disable kryten-bingo
sudo rm /etc/systemd/system/kryten-bingo.service
sudo systemctl daemon-reload
```

### Remove Files

```bash
sudo rm -rf /opt/kryten-bingo
sudo rm -rf /etc/kryten/bingo
sudo rm -rf /var/log/kryten-bingo
```

### Remove User

```bash
sudo userdel kryten
```
