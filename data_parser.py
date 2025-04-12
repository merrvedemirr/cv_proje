#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Parser Module
-----------------
Functions for parsing occupation and title data files.
"""


def parse_alternate_titles_file(file_path):
    """
    Parse the Alternate Titles txt file into a structured format
    
    Args:
        file_path: Path to the Alternate Titles.txt file
    
    Returns:
        List of dictionaries containing the parsed data
    """
    alternate_titles = []
    
    with open(file_path, 'r') as f:
        # Skip the header line
        next(f)
        
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Split line by whitespace
            parts = line.split()
            
            if len(parts) < 4:
                continue
                
            # The first part is the O*NET-SOC code
            onet_soc_code = parts[0]
            
            # Extract the source
            source_index = -1
            for i, part in enumerate(parts):
                if part.startswith("n/a") or part.startswith("CEO") or part.startswith("CAO") or \
                   part.startswith("CFO") or part.startswith("CIO") or part.startswith("CNO") or \
                   part.startswith("COO") or part.startswith("CTO") or part.startswith("EVP") or \
                   part.startswith("Hospital"):
                    source_index = i
                    break
            
            if source_index == -1:
                continue
                
            # The alternate title is everything between code and source
            alternate_title = " ".join(parts[1:source_index])
            
            # The source information
            source = " ".join(parts[source_index:])
            
            alternate_titles.append({
                'onet_soc_code': onet_soc_code,
                'alternate_title': alternate_title,
                'source': source
            })
    
    return alternate_titles


def parse_occupation_data_file(file_path):
    """
    Parse the Occupation Data txt file into a structured format
    
    Args:
        file_path: Path to the Occupation Data.txt file
    
    Returns:
        Dictionary mapping O*NET-SOC codes to occupation data
    """
    occupation_data = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Skip the header line
        next(f)
        
        current_code = None
        current_title = None
        current_description = ""
        
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts with an O*NET-SOC code pattern (nn-nnnn.nn)
            if len(line) > 8 and line[2] == '-' and line[7] == '.':
                # If we have a previous code, save it before moving to the next
                if current_code:
                    occupation_data[current_code] = {
                        'title': current_title,
                        'description': current_description.strip()
                    }
                
                # Extract the new code and title
                parts = line.split('\t')
                if len(parts) >= 2:
                    current_code = parts[0].strip()
                    current_title = parts[1].strip()
                    
                    # Initialize description - it might be on this line or subsequent lines
                    if len(parts) >= 3:
                        current_description = parts[2].strip()
                    else:
                        current_description = ""
            else:
                # This is a continuation of the description
                current_description += " " + line
        
        # Don't forget to save the last entry
        if current_code:
            occupation_data[current_code] = {
                'title': current_title,
                'description': current_description.strip()
            }
    
    return occupation_data


def find_primary_occupation(alternate_title_item, occupation_data):
    """
    Find the primary occupation data for an alternate title
    
    Args:
        alternate_title_item: Dictionary containing information about an alternate title
        occupation_data: Dictionary mapping O*NET-SOC codes to occupation data
    
    Returns:
        Dictionary containing primary occupation information or None if not found
    """
    onet_code = alternate_title_item['onet_soc_code']
    
    if onet_code in occupation_data:
        return {
            'onet_soc_code': onet_code,
            'primary_title': occupation_data[onet_code]['title'],
            'description': occupation_data[onet_code]['description']
        }
    
    return None