"""NTFY notification module."""
import logging
import requests

logger = logging.getLogger(__name__)

# Maximum length of subject to show in logs
MAX_LOG_SUBJECT_LENGTH = 50


class NtfyNotifier:
    """Handler for sending notifications to NTFY."""
    
    def __init__(self, topic_url, title="", icon="", priority=3):
        """Initialize NTFY notifier.
        
        Args:
            topic_url: The NTFY topic URL
            title: Optional notification title
            icon: Optional notification icon/tag
            priority: Priority level (1-5, default 3)
        """
        self.topic_url = topic_url
        self.title = title
        self.icon = icon
        self.priority = self._validate_priority(priority)
        logger.info(f"NTFY notifier initialized for topic: {topic_url}")
    
    def _validate_priority(self, priority):
        """Validate and normalize priority value.
        
        Args:
            priority: Priority value to validate
            
        Returns:
            Valid priority value (1-5)
        """
        try:
            priority_int = int(priority)
            if 1 <= priority_int <= 5:
                return priority_int
            else:
                logger.warning(f"Invalid priority {priority}, using default 3")
                return 3
        except (ValueError, TypeError):
            logger.warning(f"Invalid priority {priority}, using default 3")
            return 3
    
    def send_notification(self, subject, sender=None):
        """Send a notification to NTFY.
        
        Args:
            subject: The message subject to send
            sender: The sender name/email (used as title if NTFY_TITLE is not set)
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            # Use JSON body to correctly handle non-ASCII characters (e.g. umlauts)
            # in the title field, which HTTP headers cannot transmit as UTF-8.
            payload = {
                "message": subject,
                "priority": self.priority,
            }

            # Use sender as title if no explicit title is configured
            if self.title:
                payload["title"] = self.title
            elif sender:
                payload["title"] = sender

            if self.icon:
                payload["tags"] = [self.icon]

            response = requests.post(
                self.topic_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Notification sent: {subject[:MAX_LOG_SUBJECT_LENGTH]}")
                return True
            else:
                logger.error(f"Failed to send notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
