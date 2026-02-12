"""NTFY notification module."""
import logging
import requests

logger = logging.getLogger(__name__)


class NtfyNotifier:
    """Handler for sending notifications to NTFY."""
    
    def __init__(self, topic_url, title="", icon=""):
        """Initialize NTFY notifier.
        
        Args:
            topic_url: The NTFY topic URL
            title: Optional notification title
            icon: Optional notification icon URL
        """
        self.topic_url = topic_url
        self.title = title
        self.icon = icon
        logger.info(f"NTFY notifier initialized for topic: {topic_url}")
    
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
                headers["Icon"] = self.icon
            
            response = requests.post(
                self.topic_url,
                data=subject.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Notification sent: {subject[:50]}...")
                return True
            else:
                logger.error(f"Failed to send notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
