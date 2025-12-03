# Bulk Email Sender with Streamlit

A professional bulk email sender application built with Streamlit, Gmail SMTP, and MongoDB.

## Features

- 📧 **Bulk Email Sending** - Send personalized emails to multiple recipients
- 📊 **Campaign Management** - Track and manage email campaigns
- 🎨 **Multiple Templates** - Choose from 4 professional email templates:
  - Professional - Clean business communications
  - Marketing - Eye-catching promotional emails
  - Newsletter - Modern newsletter updates
  - Announcement - Bold important announcements
- 📁 **CSV Upload** - Easy recipient management via CSV files
- 📈 **Analytics** - Track sent, failed, and success rates
- ✨ **Personalization** - Use merge fields for personalized content
- 🧪 **Test Emails** - Send test emails before launching campaigns

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your credentials in `.env` file (already set up)

## Usage

Run the application:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## CSV Format

Your CSV file should contain at least an `email` column. Additional columns can be used for personalization:

```csv
email,name,company
john@example.com,John Doe,Acme Corp
jane@example.com,Jane Smith,Tech Inc
```

## Workflow

1. **Upload CSV** - Upload your recipients list
2. **Select Template** - Choose from 4 professional templates
3. **Customize** - Personalize subject and content
4. **Send** - Review and send your campaign

## Template Variables

Templates support merge fields using `{variable_name}` syntax. Common variables:
- `{name}` - Recipient's name
- `{email}` - Recipient's email
- `{company}` - Company name
- Custom fields from your CSV

## Rate Limiting

Gmail has sending limits. The app includes rate limiting (30 emails/minute by default) to stay within Gmail's quotas.

## Database

Campaigns and email logs are stored in MongoDB for tracking and analytics.

## Pages

- **Dashboard** - Overview of campaigns and statistics
- **New Campaign** - Create and send new email campaigns
- **Campaign History** - View past campaigns and logs
- **Templates** - Manage email templates

## Support

For issues or questions, check the campaign history for detailed logs of email delivery.
