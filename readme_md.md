# Resume Analysis System

This system analyzes PDF resumes to extract work experience, match job titles to standard occupational classifications, and calculate total work experience.

## Project Structure

```
resume_analysis/
│
├── main.py                    # Main application entry point
├── pdf_parser.py              # PDF extraction functionality
├── date_utils.py              # Date and duration calculation utilities
├── data_parser.py             # Functions for parsing various data files
├── matching.py                # Job title matching with BERT embeddings
├── output_formatter.py        # Output formatting utilities
└── requirements.txt           # Dependencies
```

## Features

- Extracts structured text from PDF resumes
- Identifies company names, job titles, and employment dates
- Calculates work duration for each position
- Matches job titles to standardized O*NET-SOC occupation codes using BERT embeddings
- Groups positions by occupation
- Calculates total experience for each occupation type
- Generates a comprehensive analysis report

## Requirements

- Python 3.7+
- Required libraries listed in `requirements.txt`

## Setup

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure you have the required data files in the same directory:
   - `Alternate Titles.txt` - Contains job title mappings to O*NET-SOC codes
   - `Occupation Data.txt` - Contains detailed information for each O*NET-SOC code

## Usage

```
python main.py
```

By default, the program will:
1. Analyze `Profile2.pdf` in the current directory
2. Generate an analysis report as `resume_analysis_output.txt`

## Module Descriptions

### main.py
Entry point that coordinates the analysis workflow.

### pdf_parser.py
Contains the `PDFPageDetailedAggregator` class and functions to extract and structure text from PDFs.

### date_utils.py
Utilities for parsing dates and calculating work durations.

### data_parser.py
Functions for parsing O*NET-SOC data files.

### matching.py
Functions for matching job titles to standard occupations using BERT embeddings.

### output_formatter.py
Functions for formatting and displaying analysis results.

## Output

The analysis generates a report with:
- Contact information
- Detailed work experience with matched job titles
- Total work experience calculation
- Positions grouped by occupation type

## Customization

To analyze a different resume:
- Modify the file path in the `main()` function call in `main.py`
- Adjust the parsing logic in `pdf_parser.py` if needed for different resume formats
