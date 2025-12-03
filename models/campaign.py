from datetime import datetime
from typing import List, Dict, Optional

class Campaign:
    """Campaign data model"""
    
    def __init__(
        self,
        name: str,
        subject: str,
        template_id: str,
        recipients_count: int,
        status: str = 'draft',
        created_at: Optional[datetime] = None,
        campaign_id: Optional[str] = None
    ):
        self.campaign_id = campaign_id
        self.name = name
        self.subject = subject
        self.template_id = template_id
        self.recipients_count = recipients_count
        self.status = status
        self.created_at = created_at or datetime.now()
        self.sent_count = 0
        self.failed_count = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return {
            'name': self.name,
            'subject': self.subject,
            'template_id': self.template_id,
            'recipients_count': self.recipients_count,
            'status': self.status,
            'created_at': self.created_at,
            'sent_count': self.sent_count,
            'failed_count': self.failed_count
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Campaign':
        """Create from dictionary"""
        return Campaign(
            campaign_id=str(data.get('_id')),
            name=data['name'],
            subject=data['subject'],
            template_id=data['template_id'],
            recipients_count=data['recipients_count'],
            status=data.get('status', 'draft'),
            created_at=data.get('created_at')
        )


class EmailLog:
    """Email log data model"""
    
    def __init__(
        self,
        campaign_id: str,
        recipient_email: str,
        recipient_data: Dict,
        status: str = 'pending',
        error_message: Optional[str] = None,
        sent_at: Optional[datetime] = None
    ):
        self.campaign_id = campaign_id
        self.recipient_email = recipient_email
        self.recipient_data = recipient_data
        self.status = status
        self.error_message = error_message
        self.sent_at = sent_at or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return {
            'campaign_id': self.campaign_id,
            'recipient_email': self.recipient_email,
            'recipient_data': self.recipient_data,
            'status': self.status,
            'error_message': self.error_message,
            'sent_at': self.sent_at
        }


class Template:
    """Email template data model"""
    
    def __init__(
        self,
        name: str,
        html_content: str,
        description: str = '',
        variables: Optional[List[str]] = None,
        template_id: Optional[str] = None
    ):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.html_content = html_content
        self.variables = variables or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return {
            'name': self.name,
            'description': self.description,
            'html_content': self.html_content,
            'variables': self.variables
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Template':
        """Create from dictionary"""
        return Template(
            template_id=str(data.get('_id')),
            name=data['name'],
            description=data.get('description', ''),
            html_content=data['html_content'],
            variables=data.get('variables', [])
        )
