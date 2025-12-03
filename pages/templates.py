import streamlit as st
from services import TemplateService
from models import Template

def show():
    """Templates Management Page"""
    st.markdown('<h1 class="main-header">🎨 Email Templates</h1>', unsafe_allow_html=True)
    
    template_service = TemplateService()
    
    # Tabs
    tab1, tab2 = st.tabs(["📚 View Templates", "➕ Create Template"])
    
    with tab1:
        show_templates_list(template_service)
    
    with tab2:
        show_create_template(template_service)

def show_templates_list(template_service):
    """Display all templates"""
    st.subheader("Available Templates")
    
    try:
        templates = template_service.get_all_templates()
        
        if not templates:
            st.warning("No templates found in database.")
            
            # Add button to initialize default templates
            if st.button("🔄 Initialize Default Templates", type="primary"):
                with st.spinner("Creating default templates..."):
                    template_service.initialize_default_templates()
                    st.success("✅ Default templates created!")
                    st.rerun()
            return
        
        st.success(f"Found {len(templates)} template(s)")
        
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
        st.info("Make sure MongoDB is connected properly.")
        return
    
    for template in templates:
        with st.expander(f"📄 {template.name}", expanded=False):
            st.write(f"**Description:** {template.description}")
            st.write(f"**Variables:** {', '.join(template.variables)}")
            
            # Preview
            with st.container():
                st.markdown("**Preview:**")
                sample_data = {var: f"{{{var}}}" for var in template.variables}
                st.markdown(template.html_content.format(**sample_data), unsafe_allow_html=True)
            
            # Actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Edit", key=f"edit_{template.template_id}", use_container_width=True):
                    st.session_state.editing_template = template
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{template.template_id}", use_container_width=True):
                    template_service.delete_template(template.template_id)
                    st.success(f"Deleted template: {template.name}")
                    st.rerun()

def show_create_template(template_service):
    """Create new template"""
    st.subheader("Create New Template")
    
    # Check if editing
    editing_template = st.session_state.get('editing_template', None)
    
    if editing_template:
        st.info(f"Editing: {editing_template.name}")
        default_name = editing_template.name
        default_desc = editing_template.description
        default_html = editing_template.html_content
    else:
        default_name = ""
        default_desc = ""
        default_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello {name}!</h1>
        <p>{message}</p>
        <p>Best regards,<br>{sender_name}</p>
    </div>
</body>
</html>"""
    
    name = st.text_input("Template Name", value=default_name, placeholder="e.g., My Custom Template")
    description = st.text_area("Description", value=default_desc, placeholder="Brief description of this template")
    
    st.markdown("**HTML Content** (Use {variable_name} for placeholders)")
    html_content = st.text_area(
        "HTML Content",
        value=default_html,
        height=300,
        label_visibility="collapsed"
    )
    
    # Extract variables
    if html_content:
        variables = template_service.extract_variables(html_content)
        st.success(f"Detected variables: {', '.join(variables) if variables else 'None'}")
    
    # Preview
    if st.checkbox("Show Preview"):
        st.markdown("### Preview")
        sample_data = {var: f"[{var.upper()}]" for var in variables}
        try:
            preview = template_service.render_template(html_content, sample_data)
            st.markdown(preview, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    
    # Save button
    col1, col2 = st.columns(2)
    
    with col1:
        if editing_template and st.button("Cancel", use_container_width=True):
            del st.session_state.editing_template
            st.rerun()
    
    with col2:
        button_label = "Update Template" if editing_template else "Create Template"
        
        if st.button(button_label, type="primary", use_container_width=True):
            if name and html_content:
                template = Template(
                    name=name,
                    description=description,
                    html_content=html_content,
                    variables=variables
                )
                
                if editing_template:
                    template_service.update_template(editing_template.template_id, template)
                    st.success(f"✅ Updated template: {name}")
                    del st.session_state.editing_template
                else:
                    template_service.create_template(template)
                    st.success(f"✅ Created template: {name}")
                
                st.rerun()
            else:
                st.error("Please fill in all fields")
