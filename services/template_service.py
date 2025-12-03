import re
from typing import List, Dict
from database import mongodb
from models import Template

class TemplateService:
    """Email template management service"""
    
    def __init__(self):
        self.db = mongodb
    
    def get_all_templates(self) -> List[Template]:
        """Get all available templates"""
        templates = list(self.db.templates.find())
        return [Template.from_dict(t) for t in templates]
    
    def get_template(self, template_id: str) -> Template:
        """Get a specific template by ID"""
        from bson.objectid import ObjectId
        template_data = self.db.templates.find_one({'_id': ObjectId(template_id)})
        if template_data:
            return Template.from_dict(template_data)
        return None
    
    def create_template(self, template: Template) -> str:
        """Create a new template"""
        result = self.db.templates.insert_one(template.to_dict())
        return str(result.inserted_id)
    
    def update_template(self, template_id: str, template: Template):
        """Update existing template"""
        from bson.objectid import ObjectId
        self.db.templates.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': template.to_dict()}
        )
    
    def delete_template(self, template_id: str):
        """Delete a template"""
        from bson.objectid import ObjectId
        self.db.templates.delete_one({'_id': ObjectId(template_id)})
    
    def extract_variables(self, content: str) -> List[str]:
        """Extract template variables from content"""
        # Find all {variable} patterns
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, content)
        return list(set(variables))  # Remove duplicates
    
    def render_template(self, template_html: str, data: Dict) -> str:
        """Render template with provided data"""
        try:
            return template_html.format(**data)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {str(e)}")
    
    def initialize_default_templates(self):
        """Initialize default email templates if not exists"""
        if self.db.templates.count_documents({}) == 0:
            default_templates = self._get_default_templates()
            for template in default_templates:
                self.create_template(template)
    
    def _get_default_templates(self) -> List[Template]:
        """Get default template variants"""
        return [
            Template(
                name="Professional",
                description="Clean, professional template for business communications",
                html_content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }}
        .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Hello {name}!</h1>
        </div>
        <div class="content">
            <p>Dear {name},</p>
            <p>{message}</p>
            <p>Best regards,<br>{sender_name}</p>
        </div>
        <div class="footer">
            <p>This email was sent to {email}</p>
        </div>
    </div>
</body>
</html>
                """,
                variables=['name', 'email', 'message', 'sender_name']
            ),
            Template(
                name="Marketing",
                description="Eye-catching template for marketing campaigns",
                html_content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 40px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 32px; }}
        .content {{ padding: 40px; }}
        .highlight {{ background: #fff3cd; padding: 20px; border-left: 4px solid #f5576c; margin: 20px 0; }}
        .cta {{ text-align: center; padding: 30px; }}
        .cta-button {{ display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 16px; }}
        .footer {{ background: #333; color: white; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Special Offer for {name}!</h1>
        </div>
        <div class="content">
            <p>Hi {name},</p>
            <div class="highlight">
                <p><strong>{offer_title}</strong></p>
                <p>{offer_details}</p>
            </div>
            <p>{message}</p>
            <div class="cta">
                <a href="{cta_url}" class="cta-button">{cta_text}</a>
            </div>
        </div>
        <div class="footer">
            <p>{company_name} | {email}</p>
        </div>
    </div>
</body>
</html>
                """,
                variables=['name', 'email', 'offer_title', 'offer_details', 'message', 'cta_url', 'cta_text', 'company_name']
            ),
            Template(
                name="Newsletter",
                description="Modern newsletter template for regular updates",
                html_content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Georgia, serif; margin: 0; padding: 0; background: #f8f9fa; }}
        .container {{ max-width: 650px; margin: 20px auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ background: #2c3e50; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .subtitle {{ color: #ecf0f1; margin-top: 10px; }}
        .article {{ padding: 30px; border-bottom: 1px solid #ecf0f1; }}
        .article h2 {{ color: #2c3e50; margin-top: 0; }}
        .article-meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 15px; }}
        .read-more {{ color: #3498db; text-decoration: none; font-weight: bold; }}
        .footer {{ background: #ecf0f1; padding: 20px; text-align: center; color: #7f8c8d; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{newsletter_title}</h1>
            <div class="subtitle">{date}</div>
        </div>
        <div class="article">
            <h2>Hello {name}!</h2>
            <p>{introduction}</p>
        </div>
        <div class="article">
            <h2>{article_title}</h2>
            <div class="article-meta">By {author}</div>
            <p>{article_content}</p>
            <a href="{article_url}" class="read-more">Read More →</a>
        </div>
        <div class="footer">
            <p>You're receiving this because you subscribed at {company_name}</p>
            <p>{email}</p>
        </div>
    </div>
</body>
</html>
                """,
                variables=['name', 'email', 'newsletter_title', 'date', 'introduction', 'article_title', 'author', 'article_content', 'article_url', 'company_name']
            ),
            Template(
                name="Announcement",
                description="Bold template for important announcements",
                html_content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a1a; }}
        .container {{ max-width: 600px; margin: 30px auto; }}
        .badge {{ background: #ff6b6b; color: white; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 20px; }}
        .main {{ background: white; padding: 40px; border-radius: 10px; }}
        .main h1 {{ color: #2d3436; margin-top: 0; font-size: 36px; }}
        .highlight-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin: 25px 0; }}
        .highlight-box h2 {{ margin-top: 0; }}
        .details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #95a5a6; margin-top: 30px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main">
            <div class="badge">ANNOUNCEMENT</div>
            <h1>Hi {name}! 👋</h1>
            <p>{opening_message}</p>
            
            <div class="highlight-box">
                <h2>{announcement_title}</h2>
                <p>{announcement_details}</p>
            </div>
            
            <div class="details">
                <p><strong>What this means for you:</strong></p>
                <p>{impact_description}</p>
            </div>
            
            <p>{closing_message}</p>
            <p>Best regards,<br><strong>{sender_name}</strong></p>
        </div>
        <div class="footer">
            <p>Sent to {email}</p>
        </div>
    </div>
</body>
</html>
                """,
                variables=['name', 'email', 'opening_message', 'announcement_title', 'announcement_details', 'impact_description', 'closing_message', 'sender_name']
            )
        ]
