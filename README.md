# imap-ntfy

A lightweight Python service that monitors IMAP mailboxes and sends notifications for new unread messages via [NTFY](https://ntfy.sh).

**Features:** Monitors any IMAP server (Gmail, Outlook, self-hosted), tracks processed messages in SQLite/MySQL, fully configurable via environment variables, Docker support.

## Quick Start

1. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your IMAP and NTFY settings
```

2. Start with Docker Compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

## Configuration

Configure via environment variables in `.env` file.

**Required:**
- `IMAP_HOST` - IMAP server hostname
- `IMAP_USER` - IMAP username/email
- `IMAP_PASS` - IMAP password
- `NTFY_TOPIC` - Full NTFY topic URL (e.g., `https://ntfy.sh/mytopic`)

**Optional:**
- `IMAP_PORT` - IMAP port (default: `993`)
- `IMAP_SSL` - Use SSL/TLS (default: `true`)
- `IMAP_FOLDERS` - Folders to monitor (default: `INBOX`)
- `CHECK_INTERVAL` - Check interval in seconds (default: `300`)
- `NTFY_TITLE` - Notification title
- `NTFY_ICON` - Notification icon URL (default: `envelope`)
- `NTFY_PRIORITY` - Priority level 1-5 (default: `3`)
- `DATABASE_URL` - Database connection (default: `sqlite:///messages.db`)

See `.env.example` for more details.

## How It Works

1. **Initial Run**: Marks all existing unread messages as processed (no spam from old messages)
2. **Continuous Monitoring**: Polls folders at configured interval
3. **New Messages**: Sends NTFY notifications and stores message IDs to prevent duplicates
4. **Persistence**: All processed messages stored in database

## Examples

**Gmail:**
```bash
IMAP_HOST=imap.gmail.com
IMAP_USER=your-email@gmail.com
IMAP_PASS=your-app-password  # Use App Password, not regular password
```

**ProtonMail Bridge:**
```yaml
services:
  protonmail-bridge:
    image: shenxn/protonmail-bridge:latest
    container_name: protonmail-bridge
    restart: unless-stopped
    volumes:
      - protonmail_bridge:/root

  imap-ntfy:
    image: quay.io/fabian-st/imap-ntfy:latest
    container_name: protonmail-ntfy
    restart: unless-stopped
    depends_on:
      - protonmail-bridge
    volumes:
      - protonmail_ntfy:/data
    environment:
      - IMAP_HOST=protonmail-bridge
      - IMAP_PORT=143
      - IMAP_SSL=false
      - IMAP_USER=user@proton.me
      - IMAP_PASS=secretpassword
      - NTFY_TOPIC=https://ntfy.sh/mytopic
      - IMAP_FOLDERS=INBOX,Folders/Important

volumes:
  protonmail_bridge:
  protonmail_ntfy:
```

## License

MIT License - see repository for details.
