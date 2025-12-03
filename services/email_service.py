import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
from typing import Dict, List, Optional
import streamlit as st
from config import config

class EmailService:
    """Gmail SMTP email service"""
    
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.email = config.GMAIL_EMAIL
        self.password = config.GMAIL_APP_PASSWORD
        self.rate_limit = config.RATE_LIMIT_EMAILS_PER_MINUTE
    
    def _create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            return server
        except Exception as e:
            raise Exception(f"Failed to connect to SMTP server: {str(e)}")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send a single email
        
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach files if any
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {filepath.split("/")[-1]}'
                            )
                            msg.attach(part)
                    except Exception as e:
                        print(f"Failed to attach file {filepath}: {str(e)}")
            
            # Send email
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def send_bulk_emails(
        self,
        recipients: List[Dict],
        subject: str,
        html_template: str,
        progress_callback=None
    ) -> Dict:
        """
        Send bulk emails with rate limiting
        
        Args:
            recipients: List of dicts with 'email' and other merge fields
            subject: Email subject (can include {variables})
            html_template: HTML template with {variables}
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dict with sent_count, failed_count, and errors list
        """
        results = {
            'sent_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        total = len(recipients)
        emails_this_minute = 0
        minute_start = time.time()
        
        for i, recipient in enumerate(recipients):
            # Rate limiting
            if emails_this_minute >= self.rate_limit:
                elapsed = time.time() - minute_start
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    if progress_callback:
                        progress_callback(
                            i, total, 
                            f"Rate limit reached. Waiting {int(wait_time)}s..."
                        )
                    time.sleep(wait_time)
                emails_this_minute = 0
                minute_start = time.time()
            
            # Personalize content
            personalized_subject = subject.format(**recipient)
            personalized_html = html_template.format(**recipient)
            
            # Send email
            success, error = self.send_email(
                to_email=recipient['email'],
                subject=personalized_subject,
                html_content=personalized_html
            )
            
            if success:
                results['sent_count'] += 1
            else:
                results['failed_count'] += 1
                results['errors'].append({
                    'email': recipient['email'],
                    'error': error
                })
            
            emails_this_minute += 1
            
            # Progress update
            if progress_callback:
                progress_callback(i + 1, total, f"Sent to {recipient['email']}")
        
        return results
    
    def send_test_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> tuple[bool, Optional[str]]:
        """Send a test email"""
        return self.send_email(to_email, subject, html_content)
