import streamlit as st
from datetime import datetime
from database import mongodb
from services import EmailService, TemplateService
from utils import CSVParser
from models import Campaign, EmailLog
import pandas as pd

def show():
    """New Campaign Page"""
    st.markdown('<h1 class="main-header">✉️ Create New Campaign</h1>', unsafe_allow_html=True)
    
    # Initialize services
    email_service = EmailService()
    template_service = TemplateService()
    
    # Campaign creation wizard
    if 'campaign_step' not in st.session_state:
        st.session_state.campaign_step = 1
    
    # Progress indicator
    steps = ["Upload CSV", "Select Template", "Customize Email", "Review & Send"]
    current_step = st.session_state.campaign_step
    
    cols = st.columns(4)
    for i, step_name in enumerate(steps, 1):
        with cols[i-1]:
            if i < current_step:
                st.markdown(f"✅ **{step_name}**")
            elif i == current_step:
                st.markdown(f"🔵 **{step_name}**")
            else:
                st.markdown(f"⚪ {step_name}")
    
    st.markdown("---")
    
    # Step 1: Upload CSV
    if current_step == 1:
        show_step_upload_csv()
    
    # Step 2: Select Template
    elif current_step == 2:
        show_step_select_template(template_service)
    
    # Step 3: Customize Email
    elif current_step == 3:
        show_step_customize_email(template_service)
    
    # Step 4: Review and Send
    elif current_step == 4:
        show_step_review_send(email_service, template_service)

def show_step_upload_csv():
    """Step 1: Upload and validate CSV"""
    st.subheader("📁 Upload Recipients CSV File")
    
    st.info("📋 Your CSV should contain an 'email' column. Additional columns can be used for personalization (e.g., name, company).")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file:
        # Parse CSV
        success, df, error = CSVParser.parse_csv(uploaded_file)
        
        if not success:
            st.error(f"❌ {error}")
            return
        
        # Validate emails
        valid_df, invalid_emails = CSVParser.validate_emails(df)
        
        # Show preview
        st.success(f"✅ Found {len(valid_df)} valid recipients")
        
        if invalid_emails:
            with st.expander(f"⚠️ {len(invalid_emails)} invalid email(s) found (will be skipped)"):
                for email in invalid_emails:
                    st.write(f"- {email}")
        
        # Show data preview
        st.subheader("📊 Data Preview")
        st.dataframe(valid_df.head(10), use_container_width=True)
        
        st.markdown(f"**Total Recipients:** {len(valid_df)}")
        st.markdown(f"**Available Fields:** {', '.join(CSVParser.get_available_fields(valid_df))}")
        
        # Save to session state
        st.session_state.recipients_df = valid_df
        st.session_state.recipients = CSVParser.prepare_recipients(valid_df)
        st.session_state.available_fields = CSVParser.get_available_fields(valid_df)
        
        # Next button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next: Select Template →", type="primary", use_container_width=True):
            st.session_state.campaign_step = 2
            st.rerun()

def show_step_select_template(template_service):
    """Step 2: Select email template"""
    st.subheader("🎨 Select Email Template")
    
    # Get all templates
    templates = template_service.get_all_templates()
    
    if not templates:
        st.error("No templates found. Please contact administrator.")
        return
    
    # Template selection
    cols = st.columns(2)
    
    for i, template in enumerate(templates):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"### {template.name}")
                st.markdown(template.description)
                
                # Show required variables
                with st.expander("Required Fields"):
                    st.write(", ".join(template.variables))
                
                if st.button(f"Select {template.name}", key=f"select_{template.template_id}", use_container_width=True):
                    st.session_state.selected_template = template
                    st.session_state.campaign_step = 3
                    st.rerun()
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back", use_container_width=True):
        st.session_state.campaign_step = 1
        st.rerun()

def show_step_customize_email(template_service):
    """Step 3: Customize email content"""
    st.subheader("✍️ Customize Your Email")
    
    template = st.session_state.selected_template
    
    st.info(f"Selected Template: **{template.name}**")
    
    # Campaign details
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Newsletter 2024")
    
    with col2:
        subject = st.text_input("Email Subject", placeholder="Use {name} for personalization")
    
    # Template variables mapping
    st.subheader("📝 Template Field Values")
    st.write("Provide values for fields not in your CSV. Use {field_name} to reference CSV columns.")
    
    field_values = {}
    available_fields = st.session_state.available_fields
    
    # Show which fields are from CSV
    csv_fields = []
    missing_fields = []
    
    for var in template.variables:
        if var in available_fields:
            csv_fields.append(var)
        else:
            missing_fields.append(var)
    
    if csv_fields:
        st.success(f"✅ From CSV: {', '.join(csv_fields)}")
    
    if missing_fields:
        st.warning(f"⚠️ Need values for: {', '.join(missing_fields)}")
        
        for field in missing_fields:
            field_values[field] = st.text_input(
                f"{field}",
                placeholder=f"Enter value for {field}",
                key=f"field_{field}"
            )
    
    # Preview
    st.subheader("👁️ Preview")
    
    if st.session_state.recipients:
        # Get first recipient for preview
        first_recipient = st.session_state.recipients[0].copy()
        
        # Merge with field values
        preview_data = first_recipient.copy()
        preview_data.update(field_values)
        
        # Add defaults
        preview_data = CSVParser.create_sample_data(preview_data)
        
        try:
            preview_html = template_service.render_template(template.html_content, preview_data)
            preview_subject = subject.format(**preview_data) if subject else "No subject"
            
            st.write(f"**Subject:** {preview_subject}")
            with st.expander("📧 Email Preview", expanded=True):
                st.markdown(preview_html, unsafe_allow_html=True)
            
            # Save to session
            st.session_state.campaign_name = campaign_name
            st.session_state.subject = subject
            st.session_state.field_values = field_values
            
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.campaign_step = 2
            st.rerun()
    
    with col2:
        if campaign_name and subject:
            if st.button("Next: Review & Send →", type="primary", use_container_width=True):
                st.session_state.campaign_step = 4
                st.rerun()
        else:
            st.button("Fill all fields to continue", disabled=True, use_container_width=True)

def show_step_review_send(email_service, template_service):
    """Step 4: Review and send"""
    st.subheader("🚀 Review & Send Campaign")
    
    # Get data from session
    campaign_name = st.session_state.campaign_name
    subject = st.session_state.subject
    template = st.session_state.selected_template
    recipients = st.session_state.recipients
    field_values = st.session_state.field_values
    
    # Summary
    st.markdown("### 📋 Campaign Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Campaign Name:** {campaign_name}")
        st.write(f"**Subject:** {subject}")
    with col2:
        st.write(f"**Template:** {template.name}")
        st.write(f"**Recipients:** {len(recipients)}")
    
    # Test email
    st.markdown("### 🧪 Send Test Email")
    test_email = st.text_input("Test Email Address", placeholder="your@email.com")
    
    if st.button("Send Test Email"):
        if test_email:
            with st.spinner("Sending test email..."):
                # Prepare test data
                test_data = recipients[0].copy()
                test_data.update(field_values)
                test_data = CSVParser.create_sample_data(test_data)
                test_data['email'] = test_email
                
                test_html = template_service.render_template(template.html_content, test_data)
                test_subject = subject.format(**test_data)
                
                success, error = email_service.send_test_email(test_email, test_subject, test_html)
                
                if success:
                    st.success(f"✅ Test email sent to {test_email}")
                else:
                    st.error(f"❌ Failed to send: {error}")
        else:
            st.warning("Please enter a test email address")
    
    # Send campaign
    st.markdown("### 📤 Send Campaign")
    st.warning(f"⚠️ This will send {len(recipients)} emails. This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.campaign_step = 3
            st.rerun()
    
    with col2:
        if st.button("🚀 Send Campaign", type="primary", use_container_width=True):
            send_campaign(email_service, template_service, campaign_name, subject, template, recipients, field_values)

def send_campaign(email_service, template_service, campaign_name, subject, template, recipients, field_values):
    """Send the email campaign"""
    # Create campaign in database
    campaign = Campaign(
        name=campaign_name,
        subject=subject,
        template_id=template.template_id,
        recipients_count=len(recipients),
        status='sending'
    )
    
    campaign_id = mongodb.campaigns.insert_one(campaign.to_dict()).inserted_id
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    sent_count = 0
    failed_count = 0
    
    # Prepare template
    html_template = template.html_content
    
    # Add field values as defaults
    for recipient in recipients:
        for key, value in field_values.items():
            if key not in recipient or not recipient[key]:
                recipient[key] = value
        # Add sample data defaults
        recipient.update(CSVParser.create_sample_data(recipient))
    
    # Send emails
    def progress_callback(current, total, message):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"Progress: {current}/{total} - {message}")
    
    results = email_service.send_bulk_emails(
        recipients=recipients,
        subject=subject,
        html_template=html_template,
        progress_callback=progress_callback
    )
    
    # Log each email
    for recipient in recipients:
        email_log = EmailLog(
            campaign_id=str(campaign_id),
            recipient_email=recipient['email'],
            recipient_data=recipient,
            status='sent' if recipient['email'] not in [e['email'] for e in results['errors']] else 'failed',
            error_message=next((e['error'] for e in results['errors'] if e['email'] == recipient['email']), None)
        )
        mongodb.email_logs.insert_one(email_log.to_dict())
    
    # Update campaign
    mongodb.campaigns.update_one(
        {'_id': campaign_id},
        {
            '$set': {
                'status': 'completed',
                'sent_count': results['sent_count'],
                'failed_count': results['failed_count']
            }
        }
    )
    
    # Show results
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"✅ Campaign completed!")
    st.write(f"**Sent:** {results['sent_count']}")
    st.write(f"**Failed:** {results['failed_count']}")
    
    if results['errors']:
        with st.expander("View Errors"):
            for error in results['errors']:
                st.write(f"- {error['email']}: {error['error']}")
    
    # Reset wizard
    if st.button("Create Another Campaign"):
        for key in ['campaign_step', 'recipients_df', 'recipients', 'selected_template', 
                    'campaign_name', 'subject', 'field_values']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
