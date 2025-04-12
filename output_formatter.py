#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Output Formatter Module
---------------------
Functions for formatting and displaying resume analysis results.
"""
import pandas as pd

def print_position_info(company, position, start_date, end_date, duration, match_info=None):
    """
    Print position information with optional matching alternate title
    
    Args:
        company: Company name
        position: Position title
        start_date: Start date of the position
        end_date: End date of the position
        duration: Duration string (e.g., "(2 years 3 months)")
        match_info: Optional tuple of (match_dict, score) with match information
    """
    print(f"Company: {company}, Position: {position}, Date Period: {start_date} - {end_date}{duration}")
    
    # If matching information is provided, print it underneath
    if match_info:
        match, score = match_info
        print(f"  - Matched as: {match['alternate_title']} (O*NET-SOC: {match['onet_soc_code']}, Similarity: {score:.4f})")
    print()  # Add a blank line


def print_contact_information(df_1, df_0, arr_co=None):
    """
    Print contact information extracted from the resume
    
    Args:
        df_1: DataFrame containing section heading information
        df_0: DataFrame containing detailed content information
        arr_co: Optional array with parsed contact information
    """
    print("\n" + "="*50)
    print("CONTACT INFORMATION")
    print("="*50)

    # Get name information from the first row if available
    if not df_1.empty and not df_1.iloc[0].isnull().any():
        name = df_1.iloc[0].line
        print(f"Name: {name}")
    else:
        print("Name: Not Found")
    
    # Create a filtered dataframe for contact information
    df_co = df_0[df_0['Title'] == 'Contact'].copy() if 'Title' in df_0.columns else pd.DataFrame()
    
    # Initialize contact variables
    linkedin_url = ""
    email = ""
    phone = "Not Found"
    
    # Extract LinkedIn URL and email from contact section
    if not df_co.empty:
        # Search through all rows for LinkedIn related content
        for _, row in df_co.iterrows():
            line = row['line']
            if "linkedin.com" in line.lower():
                linkedin_url += line.replace("(LinkedIn)", "").strip()
            elif "(LinkedIn)" in line:
                linkedin_url += line.replace("(LinkedIn)", "").strip()
            
            # Look for email addresses
            if "@" in line and ".com" in line:
                email = line.strip()
    
        # Look for phone information
        for _, row in df_co.iterrows():
            line = row['line']
            if "(Mobile)" in line:
                parts = line.split("(")
                if len(parts) > 0:
                    num = parts[0].strip()
                    if any(c.isdigit() for c in num):  # More lenient check for phone numbers
                        phone = num
                        break
    
    # Check if we have contact arrays from the resume parsing
    if arr_co and len(arr_co) > 0 and 'contact' in arr_co[0]:
        # Combine LinkedIn parts from contact array
        for line in arr_co[0]['contact']:
            if "linkedin" in line.lower() or "(LinkedIn)" in line:
                linkedin_url += line.replace("(LinkedIn)", "").strip()
        
        # Get email from contact array if not found yet
        if not email:
            for line in arr_co[0]['contact']:
                if "@" in line and ".com" in line:
                    email = line.strip()
                    break
        
        # Get phone from contact array if not found yet
        if phone == "Not Found":
            for line in arr_co[0]['contact']:
                if "(Mobile)" in line:
                    parts = line.split("(")
                    if len(parts) > 0:
                        num = parts[0].strip()
                        if any(c.isdigit() for c in num):
                            phone = num
                            break
    
    # Print results
    print(f"Phone: {phone}")
    print(f"Email: {email}")
    print(f"LinkedIn: {linkedin_url}")
    print()