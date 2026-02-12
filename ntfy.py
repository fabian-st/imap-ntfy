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
    
    def send_notification(self, subject):
        """Send a notification to NTFY.
        
        Args:
            subject: The message subject to send
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            headers = {}
            
            if self.title:
                headers["Title"] = self.title
            
            if self.icon:
                headers["Tags"] = self.icon
            
            # Add priority header
            headers["Priority"] = str(self.priority)
            
            response = requests.post(
                self.topic_url,
                data=subject.encode('utf-8'),
                headers=headers,
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
