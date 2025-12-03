import streamlit as st
from config import Config
from database import mongodb
from services import TemplateService
import sys

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize application - connect to DB and setup templates"""
    try:
        # Validate configuration
        Config.validate()
        
        # Connect to MongoDB
        if 'db_connected' not in st.session_state:
            with st.spinner('Connecting to database...'):
                if mongodb.connect():
                    st.session_state.db_connected = True
                    
                    # Initialize default templates
                    template_service = TemplateService()
                    template_service.initialize_default_templates()
                else:
                    st.error("Failed to connect to database. Please check your MongoDB connection string.")
                    st.stop()
    except ValueError as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Initialization error: {str(e)}")
        st.stop()

def show_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.markdown("### 📧 Bulk Email Sender")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "✉️ New Campaign", "📊 Campaign History", "🎨 Templates"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("#### Settings")
        st.markdown(f"**Email:** {Config.GMAIL_EMAIL}")
        st.markdown(f"**Rate Limit:** {Config.RATE_LIMIT_EMAILS_PER_MINUTE}/min")
        
        return page

def show_dashboard():
    """Display dashboard with statistics"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
    
    # Get statistics from database
    campaigns_collection = mongodb.campaigns
    logs_collection = mongodb.email_logs
    
    total_campaigns = campaigns_collection.count_documents({})
    total_emails_sent = logs_collection.count_documents({'status': 'sent'})
    total_emails_failed = logs_collection.count_documents({'status': 'failed'})
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_campaigns}</div>
            <div class="stat-label">Total Campaigns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="stat-number">{total_emails_sent}</div>
            <div class="stat-label">Emails Sent</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
            <div class="stat-number">{total_emails_failed}</div>
            <div class="stat-label">Emails Failed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent campaigns
    st.subheader("📋 Recent Campaigns")
    
    recent_campaigns = list(campaigns_collection.find().sort('created_at', -1).limit(5))
    
    if recent_campaigns:
        for campaign in recent_campaigns:
            with st.expander(f"📧 {campaign['name']} - {campaign['status'].upper()}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Subject:** {campaign['subject']}")
                    st.write(f"**Recipients:** {campaign['recipients_count']}")
                with col2:
                    st.write(f"**Sent:** {campaign.get('sent_count', 0)}")
                    st.write(f"**Failed:** {campaign.get('failed_count', 0)}")
                st.write(f"**Created:** {campaign['created_at'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No campaigns yet. Create your first campaign!")
    
    # Quick actions
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Create New Campaign", use_container_width=True):
            st.session_state.page = "✉️ New Campaign"
            st.rerun()
    
    with col2:
        if st.button("📊 View Campaign History", use_container_width=True):
            st.session_state.page = "📊 Campaign History"
            st.rerun()

def main():
    """Main application"""
    # Initialize
    initialize_app()
    
    # Show sidebar and get selected page
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Dashboard"
    
    selected_page = show_sidebar()
    
    # Update page if changed
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()
    
    # Display selected page
    if st.session_state.page == "🏠 Dashboard":
        show_dashboard()
    elif st.session_state.page == "✉️ New Campaign":
        # Import and show new campaign page
        import pages.new_campaign as new_campaign
        new_campaign.show()
    elif st.session_state.page == "📊 Campaign History":
        # Import and show history page
        import pages.history as history
        history.show()
    elif st.session_state.page == "🎨 Templates":
        # Import and show templates page
        import pages.templates as templates
        templates.show()

if __name__ == "__main__":
    main()
