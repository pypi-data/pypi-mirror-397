# Systemd Service Files

This directory contains systemd service unit files for running kryten-bingo as a system service.

## Installation

1. Copy the service file to systemd directory:
```bash
sudo cp systemd/kryten-bingo.service /etc/systemd/system/
```

2. Reload systemd daemon:
```bash
sudo systemctl daemon-reload
```

3. Enable the service to start on boot:
```bash
sudo systemctl enable kryten-bingo
```

4. Start the service:
```bash
sudo systemctl start kryten-bingo
```

## Service Management

Check service status:
```bash
sudo systemctl status kryten-bingo
```

View logs:
```bash
sudo journalctl -u kryten-bingo -f
```

Stop the service:
```bash
sudo systemctl stop kryten-bingo
```

Restart the service:
```bash
sudo systemctl restart kryten-bingo
```

## Configuration

The service expects:
- Installation directory: `/opt/kryten-bingo`
- Configuration file: `/etc/kryten/bingo/config.json`
- User/Group: `kryten`
- Log directory: `/var/log/kryten-bingo`

Make sure to create these directories and the kryten user before starting the service.
