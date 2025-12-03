import streamlit as st
from database import mongodb
from datetime import datetime
import pandas as pd

def show():
    """Campaign History Page"""
    st.markdown('<h1 class="main-header">📊 Campaign History</h1>', unsafe_allow_html=True)
    
    # Get all campaigns
    campaigns = list(mongodb.campaigns.find().sort('created_at', -1))
    
    if not campaigns:
        st.info("📭 No campaigns yet. Create your first campaign to get started!")
        return
    
    # Summary stats
    total_campaigns = len(campaigns)
    total_sent = sum(c.get('sent_count', 0) for c in campaigns)
    total_failed = sum(c.get('failed_count', 0) for c in campaigns)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Campaigns", total_campaigns)
    with col2:
        st.metric("Total Sent", total_sent)
    with col3:
        st.metric("Total Failed", total_failed)
    
    st.markdown("---")
    
    # Filter and search
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Search campaigns", placeholder="Search by name or subject...")
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "completed", "sending", "draft", "failed"])
    
    # Filter campaigns
    filtered_campaigns = campaigns
    
    if search:
        filtered_campaigns = [
            c for c in filtered_campaigns 
            if search.lower() in c['name'].lower() or search.lower() in c['subject'].lower()
        ]
    
    if status_filter != "All":
        filtered_campaigns = [c for c in filtered_campaigns if c['status'] == status_filter]
    
    # Display campaigns
    st.subheader(f"Campaigns ({len(filtered_campaigns)})")
    
    for campaign in filtered_campaigns:
        with st.expander(
            f"📧 {campaign['name']} - {campaign['status'].upper()} ({campaign.get('sent_count', 0)}/{campaign['recipients_count']} sent)"
        ):
            # Campaign details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Campaign Name:** {campaign['name']}")
                st.write(f"**Subject:** {campaign['subject']}")
                st.write(f"**Status:** {campaign['status']}")
                st.write(f"**Created:** {campaign['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.write(f"**Total Recipients:** {campaign['recipients_count']}")
                st.write(f"**Successfully Sent:** {campaign.get('sent_count', 0)}")
                st.write(f"**Failed:** {campaign.get('failed_count', 0)}")
                
                if campaign['recipients_count'] > 0:
                    success_rate = (campaign.get('sent_count', 0) / campaign['recipients_count']) * 100
                    st.write(f"**Success Rate:** {success_rate:.1f}%")
            
            # Show email logs
            if st.button("View Details", key=f"details_{campaign['_id']}"):
                show_campaign_details(campaign['_id'])

def show_campaign_details(campaign_id):
    """Show detailed logs for a campaign"""
    st.subheader("📋 Email Logs")
    
    # Get all logs for this campaign
    logs = list(mongodb.email_logs.find({'campaign_id': str(campaign_id)}))
    
    if not logs:
        st.info("No logs found for this campaign.")
        return
    
    # Convert to dataframe
    df_data = []
    for log in logs:
        df_data.append({
            'Email': log['recipient_email'],
            'Status': log['status'],
            'Sent At': log['sent_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'Error': log.get('error_message', '-')
        })
    
    df = pd.DataFrame(df_data)
    
    # Status filter
    status_filter = st.selectbox("Filter by status", ["All", "sent", "failed"], key=f"filter_{campaign_id}")
    
    if status_filter != "All":
        df = df[df['Status'] == status_filter]
    
    # Display dataframe
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Logs as CSV",
        data=csv,
        file_name=f"campaign_logs_{campaign_id}.csv",
        mime="text/csv"
    )
