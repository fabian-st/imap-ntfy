# imap-ntfy

A lightweight Python service that monitors IMAP mailboxes and sends notifications for new unread messages via [NTFY](https://ntfy.sh).

## Features

- 📧 Connects to any IMAP server (Gmail, Outlook, self-hosted, etc.)
- 📁 Monitors multiple folders simultaneously
- 🔔 Sends notifications to NTFY for new unread messages
- 🗄️ Tracks processed messages in SQLite or MySQL database
- ⚙️ Fully configurable via environment variables
- 🐳 Docker support for easy deployment
- 🔄 Configurable polling interval
- 🎨 Customizable notification title and icon

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/fabian-st/imap-ntfy.git
cd imap-ntfy
```

2. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

3. Edit `.env` with your settings:
```bash
# IMAP Server Configuration
IMAP_HOST=imap.example.com
IMAP_PORT=993
IMAP_USERNAME=user@example.com
IMAP_PASSWORD=your_password
IMAP_FOLDERS=INBOX

# NTFY Configuration
NTFY_TOPIC=https://ntfy.sh/your-unique-topic

# Check every 60 seconds
CHECK_INTERVAL=60
```

4. Start the service:
```bash
docker-compose up -d
```

5. View logs:
```bash
docker-compose logs -f
```

### Using Docker

```bash
docker build -t imap-ntfy .

docker run -d \
  --name imap-ntfy \
  -e IMAP_HOST=imap.example.com \
  -e IMAP_USERNAME=user@example.com \
  -e IMAP_PASSWORD=your_password \
  -e NTFY_TOPIC=https://ntfy.sh/your-topic \
  -v $(pwd)/data:/data \
  imap-ntfy
```

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy and configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the application:
```bash
python main.py
```

## Configuration

All configuration is done via environment variables. You can set them in a `.env` file or pass them directly to Docker.

### IMAP Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IMAP_HOST` | Yes | - | IMAP server hostname |
| `IMAP_PORT` | No | `993` | IMAP server port |
| `IMAP_USERNAME` | Yes | - | IMAP username/email |
| `IMAP_PASSWORD` | Yes | - | IMAP password |
| `IMAP_USE_SSL` | No | `true` | Use SSL/TLS connection |
| `IMAP_FOLDERS` | No | `INBOX` | Comma-separated list of folders to monitor |

### NTFY Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NTFY_TOPIC` | Yes | - | Full NTFY topic URL (e.g., `https://ntfy.sh/mytopic`) |
| `NTFY_TITLE` | No | _(empty)_ | Notification title |
| `NTFY_ICON` | No | _(empty)_ | Notification icon URL |

### Polling Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CHECK_INTERVAL` | No | `60` | Interval in seconds between IMAP checks |

### Database Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///messages.db` | Database connection URL |

#### Database URL Examples

**SQLite** (default):
```
DATABASE_URL=sqlite:///messages.db
```

**SQLite with Docker** (persisted to volume):
```
DATABASE_URL=sqlite:////data/messages.db
```

**MySQL**:
```
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

## How It Works

1. **Initial Run**: On first start, the service connects to your IMAP server and marks all existing unread messages as "processed" without sending notifications. This prevents notification spam from old messages.

2. **Continuous Monitoring**: The service then polls your configured folders at the specified interval (default: 60 seconds).

3. **New Message Detection**: When a new unread message arrives, the service:
   - Extracts the message subject
   - Sends a notification to your NTFY topic
   - Stores the message ID in the database to prevent duplicate notifications

4. **Persistence**: All processed message IDs are stored in the database, ensuring notifications are only sent once per message, even if the service restarts.

## Examples

### Multiple Folders

Monitor both INBOX and a Spam folder:
```bash
IMAP_FOLDERS=INBOX,Spam
```

### Custom Notification Appearance

```bash
NTFY_TOPIC=https://ntfy.sh/my-email-alerts
NTFY_TITLE=📧 New Email
NTFY_ICON=https://example.com/email-icon.png
```

### Gmail Configuration

```bash
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_USE_SSL=true
```

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### Outlook/Office 365 Configuration

```bash
IMAP_HOST=outlook.office365.com
IMAP_PORT=993
IMAP_USERNAME=your-email@outlook.com
IMAP_PASSWORD=your-password
IMAP_USE_SSL=true
```

## Troubleshooting

### Viewing Logs

**Docker Compose**:
```bash
docker-compose logs -f
```

**Docker**:
```bash
docker logs -f imap-ntfy
```

### Common Issues

**"Missing required configuration" error**: Make sure all required environment variables are set (IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD, NTFY_TOPIC).

**IMAP connection fails**: 
- Verify your IMAP server hostname and port
- Check if your email provider requires app-specific passwords
- Ensure IMAP access is enabled in your email account settings

**No notifications received**:
- Verify your NTFY topic URL is correct
- Check that new messages are arriving and marked as unread
- Review the logs for any errors

**Database errors**:
- For SQLite with Docker, ensure the volume is properly mounted
- For MySQL, verify the connection string and credentials

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
