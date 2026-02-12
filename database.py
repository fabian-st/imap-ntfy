"""Database module for storing processed message IDs."""
import logging
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

Base = declarative_base()


class ProcessedMessage(Base):
    """Model for storing processed message IDs."""
    __tablename__ = 'processed_messages'
    
    message_id = Column(String(255), primary_key=True)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Database:
    """Database handler for message tracking."""
    
    def __init__(self, database_url):
        """Initialize database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"Database initialized: {database_url.split(':')[0]}")
    
    def is_processed(self, message_id):
        """Check if a message has been processed.
        
        Args:
            message_id: The message ID to check
            
        Returns:
            True if message was already processed, False otherwise
        """
        result = self.session.query(ProcessedMessage).filter_by(
            message_id=message_id
        ).first()
        return result is not None
    
    def mark_as_processed(self, message_id):
        """Mark a message as processed.
        
        Args:
            message_id: The message ID to mark as processed
        """
        try:
            message = ProcessedMessage(message_id=message_id)
            self.session.add(message)
            self.session.commit()
            logger.debug(f"Marked message as processed: {message_id}")
        except IntegrityError:
            # Message already exists (duplicate), rollback and continue
            self.session.rollback()
            logger.debug(f"Message already processed: {message_id}")
    
    def is_empty(self):
        """Check if database is empty (first run).
        
        Returns:
            True if no messages have been processed yet
        """
        count = self.session.query(ProcessedMessage).count()
        return count == 0
    
    def close(self):
        """Close database connection."""
        self.session.close()
