#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date Utilities Module
--------------------
Functions for handling dates and calculating durations in resume analysis.
"""

from datetime import datetime

# Month names to numbers mapping
MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}


def calculate_duration(start_date, end_date):
    """
    Calculate the duration between two dates in years and months
    
    Args:
        start_date (str): Start date in "Month Year" format (e.g., "June 2019")
        end_date (str): End date in "Month Year" format or "Present"
    
    Returns:
        str: Duration in "X years Y months" format or None if inputs are invalid
    """
    # Parse start date
    start_parts = start_date.split()
    if len(start_parts) != 2:
        return None
    start_month = MONTHS.get(start_parts[0])
    if not start_month:
        return None
    try:
        start_year = int(start_parts[1])
    except ValueError:
        return None
    
    # Parse end date
    if end_date == "Present":
        now = datetime.now()
        end_month = now.month
        end_year = now.year
    else:
        end_parts = end_date.split()
        if len(end_parts) != 2:
            return None
        end_month = MONTHS.get(end_parts[0])
        if not end_month:
            return None
        try:
            end_year = int(end_parts[1])
        except ValueError:
            return None
        
        # Add one month to end date if it's not "Present"
        # This change makes the calculation inclusive of the end month
        end_month += 1
        if end_month > 12:
            end_month = 1
            end_year += 1
    
    # Calculate total months
    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    
    # Convert to years and months
    years = total_months // 12
    remaining_months = total_months % 12
    
    # Format the duration
    if remaining_months == 0:
        return f"{years} year{'s' if years != 1 else ''}"
    else:
        return f"{years} year{'s' if years != 1 else ''} {remaining_months} month{'s' if remaining_months != 1 else ''}"


def calculate_total_experience_direct(all_durations):
    """
    Calculate total experience by directly summing duration strings
    
    Args:
        all_durations: List of duration strings in "X years Y months" format
    
    Returns:
        tuple: (years, months) total experience
    """
    total_years = 0
    total_months = 0
    
    for duration_str in all_durations:
        parts = duration_str.split()
        
        # Add year value
        if len(parts) >= 2 and parts[1].startswith('year'):
            try:
                years = int(parts[0])
                total_years += years
            except ValueError:
                continue
        
        # Add month value (if present)
        if len(parts) >= 4 and parts[3].startswith('month'):
            try:
                months = int(parts[2])
                total_months += months
            except ValueError:
                continue
    
    # Convert excess months to years
    additional_years = total_months // 12
    total_years += additional_years
    total_months = total_months % 12
    
    return total_years, total_months