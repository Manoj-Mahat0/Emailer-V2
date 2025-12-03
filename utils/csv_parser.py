import pandas as pd
from typing import List, Dict, Tuple
import re
from email_validator import validate_email, EmailNotValidError

class CSVParser:
    """CSV file parser and validator"""
    
    @staticmethod
    def parse_csv(file) -> Tuple[bool, pd.DataFrame, str]:
        """
        Parse uploaded CSV file
        
        Returns:
            Tuple of (success: bool, dataframe: pd.DataFrame, error_message: str)
        """
        try:
            df = pd.read_csv(file)
            
            # Check if empty
            if df.empty:
                return False, None, "CSV file is empty"
            
            # Check for email column
            email_columns = [col for col in df.columns if 'email' in col.lower()]
            if not email_columns:
                return False, None, "CSV must contain an 'email' column"
            
            # Rename first email column to 'email' for consistency
            if email_columns[0] != 'email':
                df.rename(columns={email_columns[0]: 'email'}, inplace=True)
            
            # Remove rows with empty emails
            df = df[df['email'].notna()]
            df = df[df['email'].astype(str).str.strip() != '']
            
            # Fill NaN values with empty strings
            df = df.fillna('')
            
            return True, df, ""
            
        except Exception as e:
            return False, None, f"Error parsing CSV: {str(e)}"
    
    @staticmethod
    def validate_emails(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate email addresses in dataframe
        
        Returns:
            Tuple of (valid_df: pd.DataFrame, invalid_emails: List[str])
        """
        invalid_emails = []
        valid_indices = []
        
        for idx, row in df.iterrows():
            email = row['email'].strip()
            try:
                # Validate email
                validate_email(email, check_deliverability=False)
                valid_indices.append(idx)
            except EmailNotValidError:
                invalid_emails.append(email)
        
        valid_df = df.loc[valid_indices].reset_index(drop=True)
        
        return valid_df, invalid_emails
    
    @staticmethod
    def get_column_preview(df: pd.DataFrame, max_rows: int = 5) -> str:
        """Get a preview of the CSV data"""
        return df.head(max_rows).to_html(index=False, classes='dataframe')
    
    @staticmethod
    def prepare_recipients(df: pd.DataFrame) -> List[Dict]:
        """
        Convert dataframe to list of recipient dictionaries
        
        Returns:
            List of dicts with email and other fields
        """
        recipients = []
        for _, row in df.iterrows():
            recipient = row.to_dict()
            # Ensure all values are strings and handle missing data
            recipient = {k: str(v) if v else '' for k, v in recipient.items()}
            recipients.append(recipient)
        
        return recipients
    
    @staticmethod
    def get_available_fields(df: pd.DataFrame) -> List[str]:
        """Get list of available fields from CSV"""
        return df.columns.tolist()
    
    @staticmethod
    def create_sample_data(recipient_dict: Dict) -> Dict:
        """Create sample data for template preview"""
        sample = recipient_dict.copy()
        
        # Add default values for common fields if not present
        defaults = {
            'name': sample.get('name', 'John Doe'),
            'company': sample.get('company', 'Example Corp'),
            'sender_name': 'Your Company',
            'company_name': 'Your Company',
            'message': 'This is a sample message',
            'date': pd.Timestamp.now().strftime('%B %d, %Y')
        }
        
        for key, value in defaults.items():
            if key not in sample or not sample[key]:
                sample[key] = value
        
        return sample
