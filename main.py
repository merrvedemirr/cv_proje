#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resume Analysis System - Main Module
-----------------------------------
Entry point for the resume analysis system.
"""

import sys
import pandas as pd
from collections import defaultdict
import json  # yeni eklenecek



# Import custom modules
from pdf_parser import parse_pdf_resume
from date_utils import calculate_duration, calculate_total_experience_direct
from data_parser import parse_alternate_titles_file, parse_occupation_data_file
from matching import match_all_positions_with_alternate_titles
from output_formatter import print_contact_information, print_position_info
from visualization import save_matched_titles_pie_plotly


# from visualization import plot_similarity_scores, plot_experience_by_onet, plot_position_durations


def main(resume_file='./Profile2.pdf', output_file_path='resume_analysis_output.txt'):
    """
    Main function to process resume and generate analysis
    
    Args:
        resume_file: Path to the resume PDF file
        output_file_path: Path to save the analysis output
    """
    # Redirect output to a file
    output_file = open(output_file_path, 'w', encoding='utf-8')
    sys.stdout = output_file

    try:
        # Parse the PDF resume
        df, df_1, df_0, arr, arr_co = parse_pdf_resume(resume_file)
        
        # Print contact information
        print_contact_information(df_1, df_0, arr_co)

        # Load occupation data files
        alternate_titles = parse_alternate_titles_file('./data/Alternate_Titles.txt')
        occupation_data = parse_occupation_data_file('./data/Occupation_Data.txt')
        
        # Extract all positions for batch matching
        all_positions = []
        for item in arr:
            for exp in item.get('experience', []):
                position = exp.get('position', 'Unknown Position')
                all_positions.append(position)
        
        # Get unique positions
        unique_positions = list(set(all_positions))
        
        # Match all positions at once
        print("Matching positions with alternate titles...\n")
        position_matches = match_all_positions_with_alternate_titles(unique_positions, alternate_titles, top_n=1)
        
        # Extract all positions and track which companies they belong to
        all_work_periods = []
        all_durations = []  # Track durations
        all_matches = []
        
        print("="*50)
        print("WORK EXPERIENCE WITH MATCHED TITLES")
        print("="*50 + "\n")
        
        for item in arr:
            company = item.get('company', 'Unknown Company')
            for exp in item.get('experience', []):
                position = exp.get('position', 'Unknown Position')
                
                # Get the match for this position
                match_info = position_matches.get(position, [])
                
                date_periods = exp.get('date_period', [])
                for period in date_periods:
                    start_date = period[0] if len(period) > 0 else 'Unknown Start'
                    end_date = period[1] if len(period) > 1 and period[1] else 'Present'
                    current_status = period[2] if len(period) > 2 and period[2] else ''
                    
                    # If end_date is empty but current_status has a value, use that as the end status
                    if not end_date and current_status:
                        end_date = current_status
                        current_status = ''
                    
                    # Calculate duration for this position
                    duration = ""
                    if start_date != 'Unknown Start' and end_date != 'Unknown End':
                        duration = calculate_duration(start_date, end_date)
                        if duration:
                            duration = f" ({duration})"
                            # Add duration to list - remove parentheses and spaces
                            all_durations.append(duration.strip(" ()"))
                    
                    # Print position info with match directly underneath
                    print_position_info(company, position, start_date, end_date, duration, 
                                       match_info[0] if match_info else None)
                    
                    # Add to work periods
                    if start_date != 'Unknown Start' and end_date != 'Unknown End':
                        all_work_periods.append({
                            'start': start_date,
                            'end': end_date,
                            'company': company,
                            'position': position
                        })
                    
                    # Store matches for analysis
                    if match_info:
                        match, score = match_info[0]
                        all_matches.append({
                            'position': position,
                            'company': company,
                            'match': match,
                            'score': score
                        })
        
        # Calculate total experience by directly summing durations
        direct_years, direct_months = calculate_total_experience_direct(all_durations)
        
        print("\n" + "="*50)
        print("TOTAL WORK EXPERIENCE")
        print("="*50)
        print(f"Total Work Experience: {direct_years} years and {direct_months} months")

        # Group positions by O*NET-SOC codes
        onet_code_groups = defaultdict(list)
        
        for match_info in all_matches:
            onet_code = match_info['match']['onet_soc_code']
            onet_code_groups[onet_code].append(match_info)
        
        # Find and print occupations for each code group
        print("\n" + "="*50)
        print("POSITIONS GROUPED BY O*NET-SOC CODE")
        print("="*50)
        
        for onet_code, match_infos in sorted(onet_code_groups.items()):
            # Find occupation data
            primary_occupation = None
            if onet_code in occupation_data:
                primary_occupation = occupation_data[onet_code]
                
                print(f"\nO*NET-SOC Code: {onet_code}")
                print(f"Primary Occupation: {primary_occupation['title']}")
                description_text = primary_occupation['description'] 
                print(f"Description: {description_text[:200]}..." if len(description_text) > 200 else f"Description: {description_text}")
                
                # Show positions contributing to the grouping
                print("\nMatched Positions:")
                
                # Find highest match score for each unique position
                position_scores = {}
                for match_info in match_infos:
                    position = match_info['position']
                    company = match_info['company']
                    score = match_info['score']
                    alternate_title = match_info['match']['alternate_title']
                    
                    key = f"{position} at {company}"
                    if key not in position_scores or score > position_scores[key]['score']:
                        position_scores[key] = {
                            'position': position,
                            'company': company,
                            'score': score,
                            'alternate_title': alternate_title
                        }
                
                # Sort by highest match scores
                sorted_positions = sorted(position_scores.values(), key=lambda x: x['score'], reverse=True)
                
                for pos_info in sorted_positions:
                    print(f"  • {pos_info['position']} at {pos_info['company']} (Similarity: {pos_info['score']:.4f})")
                    print(f"    Matched as: {pos_info['alternate_title']}")
                
                # Calculate total work duration for this occupation group
                occupation_durations = []
                for match_info in match_infos:
                    position = match_info['position']
                    company = match_info['company']
                    
                    # Find work durations for this position and company
                    for period in all_work_periods:
                        if period['position'] == position and period['company'] == company:
                            # Calculate duration for each position
                            duration = calculate_duration(period['start'], period['end'])
                            if duration:
                                occupation_durations.append(duration)
                    
                # Calculate total experience for this occupation using direct sum
                occupation_years, occupation_months = calculate_total_experience_direct(occupation_durations)
                
                print(f"\nTotal experience in {primary_occupation['title']}: {occupation_years} years and {occupation_months} months")
                print("-" * 50)
        #----------------
        # Web arayüzü için JSON çıktısı hazırla
        # contact_lines yerine tek metinle çalış
        web_data = {
            "contact": {
                "name": arr_co[0]['contact'][0] if arr_co else "Not Found",
                "email": next((line for line in arr_co[0]['contact'] if "@" in line and ".com" in line), "Not Found") if arr_co else "Not Found",
                "phone": next((line.split("(")[0].strip() for line in arr_co[0]['contact'] if "(Mobile)" in line), "Not Found") if arr_co else "Not Found",
                "linkedin": next((line.replace("(LinkedIn)", "").strip() for line in arr_co[0]['contact'] if "linkedin" in line.lower()), "Not Found") if arr_co else "Not Found"
            },
            "experience": [],
            "total_experience": {
            "years": direct_years,
            "months": direct_months
            }
        }

        # Deneyimleri web formatına uygun hale getir
        for item in arr:
            company = item.get('company', 'Unknown Company')
            for exp in item.get('experience', []):
                position = exp.get('position', 'Unknown Position')
                date_periods = exp.get('date_period', [])
                for period in date_periods:
                    start_date = period[0] if len(period) > 0 else 'Unknown'
                    end_date = period[1] if len(period) > 1 and period[1] else 'Present'
                    duration = calculate_duration(start_date, end_date)

                    match_info = position_matches.get(position, [])
                    match_data = None
                    score = None
                    if match_info:
                        match, score = match_info[0]
                        match_data = {
                            "alternate_title": match['alternate_title'],
                            "onet_soc_code": match['onet_soc_code']
                        }       

                    web_data["experience"].append({
                        "position": position,
                        "company": company,
                        "start": start_date,
                        "end": end_date,
                        "duration": duration if duration else "N/A",
                        "match": match_data,
                        "score": float(round(score, 4)) if score else None

                    })

        # JSON dosyasına yaz
        with open("data_output.json", "w", encoding="utf-8") as f:
            json.dump(web_data, f, indent=4, ensure_ascii=False)

        # 📊 GRAFİKLERİ ÜRET
        from visualization import (
            save_similarity_scores_bar,
            save_position_durations_bar,
            save_onet_experience_pie,
            save_matched_titles_pie,  # ⬅️ bunu ekledik
            save_position_titles_pie , # ⬅️ Yeni eklenen
            save_matched_titles_pie_plotly,  # ⬅️ BURADA
            save_career_timeline_plotly,
            save_company_durations_pie_plotly,
            save_onet_experience_pie_plotly

        )

        save_similarity_scores_bar(all_matches)
        save_position_durations_bar(all_work_periods)
        save_onet_experience_pie(onet_code_groups, all_work_periods)
        save_matched_titles_pie(all_matches, all_work_periods, occupation_data)
        save_position_titles_pie(all_work_periods)  # ⬅️ Yeni çağrı
        save_matched_titles_pie_plotly(all_matches, all_work_periods)
        save_company_durations_pie_plotly(all_work_periods)
        save_onet_experience_pie_plotly(onet_code_groups, all_work_periods, occupation_data)
        save_career_timeline_plotly(all_work_periods)



    finally:
        # Close the output file
        output_file.close()
        
        # Reset stdout to original
        sys.stdout = sys.__stdout__
        
        print(f"Analysis complete. Results have been saved to '{output_file_path}'")
        print(f"Total Work Experience: {direct_years} years and {direct_months} months")


if __name__ == "__main__":
    main()