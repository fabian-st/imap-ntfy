"""Main application for IMAP to NTFY bridge."""
import logging
import os
import sys
import time
from imapclient import IMAPClient
from dotenv import load_dotenv
from database import Database
from ntfy import NtfyNotifier, MAX_LOG_SUBJECT_LENGTH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class IMAPNtfyBridge:
    """Bridge service that monitors IMAP folders and sends notifications via NTFY."""
    
    def __init__(self):
        """Initialize the bridge service with configuration from environment."""
        # Load environment variables
        load_dotenv()
        
        # IMAP Configuration
        self.imap_host = os.getenv('IMAP_HOST')
        self.imap_port = int(os.getenv('IMAP_PORT', '993'))
        self.imap_username = os.getenv('IMAP_USERNAME')
        self.imap_password = os.getenv('IMAP_PASSWORD')
        self.imap_use_ssl = os.getenv('IMAP_USE_SSL', 'true').lower() == 'true'
        self.imap_folders = os.getenv('IMAP_FOLDERS', 'INBOX').split(',')
        
        # Polling Configuration
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '60'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '50'))
        
        # NTFY Configuration
        self.ntfy_topic = os.getenv('NTFY_TOPIC')
        self.ntfy_title = os.getenv('NTFY_TITLE', '')
        self.ntfy_icon = os.getenv('NTFY_ICON', '')
        
        # Database Configuration
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///messages.db')
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize components
        self.database = Database(self.database_url)
        self.notifier = NtfyNotifier(self.ntfy_topic, self.ntfy_title, self.ntfy_icon)
        self.is_first_run = self.database.is_empty()
        
        if self.is_first_run:
            logger.info("First run detected - will mark all existing unread messages as processed")
        
        logger.info("IMAP-NTFY Bridge initialized")
    
    def _validate_config(self):
        """Validate required configuration parameters."""
        required = {
            'IMAP_HOST': self.imap_host,
            'IMAP_USERNAME': self.imap_username,
            'IMAP_PASSWORD': self.imap_password,
            'NTFY_TOPIC': self.ntfy_topic,
        }
        
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    def connect_imap(self):
        """Connect to IMAP server.
        
        Returns:
            IMAPClient instance
        """
        logger.info(f"Connecting to IMAP server: {self.imap_host}:{self.imap_port}")
        client = IMAPClient(self.imap_host, port=self.imap_port, ssl=self.imap_use_ssl)
        client.login(self.imap_username, self.imap_password)
        logger.info("IMAP login successful")
        return client
    
    def process_folder(self, client, folder):
        """Process unread messages in a folder.
        
        Args:
            client: IMAPClient instance
            folder: Folder name to process
        """
        try:
            # Strip whitespace from folder name
            folder = folder.strip()
            
            logger.info(f"Processing folder: {folder}")
            client.select_folder(folder)
            
            # Search for unread messages
            messages = client.search(['UNSEEN'])
            logger.info(f"Found {len(messages)} unread messages in {folder}")
            
            if not messages:
                return
            
            # Process messages in batches to avoid memory issues
            for i in range(0, len(messages), self.batch_size):
                batch = messages[i:i+self.batch_size]
                logger.debug(f"Processing batch {i//self.batch_size + 1}: {len(batch)} messages")
                
                # Fetch message data for this batch
                message_data = client.fetch(batch, ['RFC822.HEADER'])
                
                for msg_id, data in message_data.items():
                    try:
                        # Get the Message-ID from headers
                        try:
                            header = data[b'RFC822.HEADER'].decode('utf-8', errors='replace')
                        except UnicodeDecodeError as e:
                            logger.warning(f"Failed to decode header for message {msg_id}: {e}")
                            continue
                        
                        message_id = self._extract_message_id(header)
                        
                        if not message_id:
                            logger.warning(f"Could not extract Message-ID for message {msg_id}")
                            continue
                        
                        # Check if already processed
                        if self.database.is_processed(message_id):
                            logger.debug(f"Message already processed: {message_id}")
                            continue
                        
                        # Extract subject
                        subject = self._extract_subject(header)
                        
                        # On first run, just mark as processed without sending notification
                        if self.is_first_run:
                            logger.info(f"First run: marking existing message as processed: {subject[:MAX_LOG_SUBJECT_LENGTH]}...")
                            self.database.mark_as_processed(message_id)
                        else:
                            # Send notification for new message
                            logger.info(f"New unread message: {subject[:MAX_LOG_SUBJECT_LENGTH]}...")
                            if self.notifier.send_notification(subject):
                                self.database.mark_as_processed(message_id)
                            else:
                                logger.error("Failed to send notification, will retry next time")
                    
                    except Exception as e:
                        logger.error(f"Error processing message {msg_id}: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error processing folder {folder}: {e}")
    
    def _extract_message_id(self, header):
        """Extract Message-ID from email header.
        
        Args:
            header: Email header string
            
        Returns:
            Message-ID or None
        """
        for line in header.split('\n'):
            if line.lower().startswith('message-id:'):
                return line.split(':', 1)[1].strip()
        return None
    
    def _extract_subject(self, header):
        """Extract subject from email header.
        
        Args:
            header: Email header string
            
        Returns:
            Subject string or "No Subject"
        """
        subject_lines = []
        in_subject = False
        
        for line in header.split('\n'):
            if line.lower().startswith('subject:'):
                subject_lines.append(line.split(':', 1)[1].strip())
                in_subject = True
            elif in_subject and line.startswith((' ', '\t')):
                # Continuation of subject line
                subject_lines.append(line.strip())
            elif in_subject:
                break
        
        if subject_lines:
            return ' '.join(subject_lines)
        return "No Subject"
    
    def run(self):
        """Run the main polling loop."""
        logger.info(f"Starting IMAP-NTFY Bridge")
        logger.info(f"Monitoring folders: {', '.join(self.imap_folders)}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        while True:
            try:
                client = self.connect_imap()
                
                # Process each configured folder
                for folder in self.imap_folders:
                    self.process_folder(client, folder)
                
                # After first run, disable first_run flag
                if self.is_first_run:
                    self.is_first_run = False
                    logger.info("First run complete - will now send notifications for new messages")
                
                client.logout()
                logger.info(f"Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info(f"Retrying in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
        
        self.database.close()
        logger.info("IMAP-NTFY Bridge stopped")


def main():
    """Main entry point."""
    try:
        bridge = IMAPNtfyBridge()
        bridge.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
