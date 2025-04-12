#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF Parser Module
----------------
Functions for extracting and parsing text from PDF resumes.
"""

import re
import pandas as pd
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage


class PDFPageDetailedAggregator(PDFPageAggregator):
    """
    Extended PDFPageAggregator that extracts detailed text position information
    """
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.page_number = 0
        
    def receive_layout(self, ltpage):
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    row = [page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str] # bbox == (x1, y1, x2, y2)
                    self.rows.append(row)
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        self.page_number += 1
        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage


def parse_pdf_resume(file_path):
    """
    Parse a PDF resume file and extract structured information
    
    Args:
        file_path: Path to the PDF resume file
        
    Returns:
        tuple: (df, df_1, df_0, arr, arr_co) - Dataframes and arrays containing parsed resume data
    """
    # Open and parse the PDF file
    fp = open(file_path, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Process each page
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        # Get the LTPage object for this page
        device.get_result()

    # Extract the rows of text
    my_array = device.rows

    # Create a DataFrame from the extracted text
    df = pd.DataFrame.from_records(my_array)
    df.columns = ['pn','x0','y0','x1','y1','line']
    df['y_dif'] = round(df['y1']-df['y0'])

    # Calculate cumulative y-coordinates for multi-page documents
    grouped_y0 = df.groupby(['pn'])['y0'].max().reset_index().sort_values('pn', ascending=True)
    grouped_y1 = df.groupby(['pn'])['y1'].max().reset_index().sort_values('pn', ascending=True)

    grouped_y0['y0_'] = grouped_y0['y0'].shift(-1)
    grouped_y1['y1_'] = grouped_y1['y1'].shift(-1)

    grouped_y0.fillna(0, inplace=True)
    grouped_y1.fillna(0, inplace=True)

    grouped_y0['cum_y0'] = grouped_y0.loc[::-1, 'y0_'].cumsum()[::-1]
    grouped_y1['cum_y1'] = grouped_y1.loc[::-1, 'y1_'].cumsum()[::-1]

    grouped_y0 = grouped_y0[['pn','cum_y0']]
    grouped_y1 = grouped_y1[['pn','cum_y1']]

    df = df.merge(grouped_y0, on='pn')
    df = df.merge(grouped_y1, on='pn')

    df['y0'] = df['y0'] + df['cum_y0']
    df['y1'] = df['y1'] + df['cum_y1']

    df.drop(['cum_y0', 'cum_y1'], axis=1, inplace=True)

    # Group text by indentation level
    indent_cat = {}
    pct = 0.001
    for index, row in df.iterrows():
        feature = row['x0']
        bin_found = False
        for bin_key,bin_arr in indent_cat.items():
            if feature >= (bin_key * (1.0-pct)) and (bin_key * (1.0+pct)) >= feature:
                bin_found = True
                bin_arr.append(index)
        if not bin_found:
            indent_cat[feature] = [index]

    def labeling(x, cat_):
        for key, val in cat_.items():
            if x in val:
                return list(sorted(cat_)).index(key)

    df['indent_label'] = df.index.map(lambda x: labeling(x, indent_cat))

    # Split DataFrame by indentation level
    df_1 = df[df['indent_label'] == 1].copy()
    df_0 = df[df['indent_label'] == 0].copy()

    # Add title information to the DataFrames
    arr = []
    def title(row):
        if row.y_dif >= 22:
            arr.append(row.line)
        return arr[-1]

    df_1['Title'] = df_1.apply(lambda row: title(row), axis=1)
    
    # Add title to df_0 as well for contact section identification
    arr_0 = []
    def title_0(row):
        if row.y_dif >= 18:
            arr_0.append(row.line)
        return arr_0[-1]
    
    df_0['Title'] = df_0.apply(lambda row: title_0(row), axis=1)

    # Extract experience and education sections
    df_ex = df_1[df_1['Title'] == 'Experience'].copy()
    df_ed = df_1[df_1['Title'] == 'Education'].copy()

    # Regular expression for parsing date ranges
    pattern = r'([a-zA-Z]+\s\d{4})\s-\s(?:([a-zA-Z]+\s\d{4})|(\w+))'
    regex = re.compile(pattern, re.IGNORECASE)

    # Parse experience section
    arr = []
    for index, row in df_ex.iterrows():
        if row['y_dif'] == 17:
            arr.append({})
            arr[-1]['company'] = row['line']
        elif row['y_dif'] == 16:
            if 'experience' not in arr[-1]:
                arr[-1]['experience'] = []
            arr[-1]['experience'].append({})
            arr[-1]['experience'][-1]['position'] = row['line']
        elif row['y_dif'] == 15 and regex.findall(row['line']):
            if 'experience' in arr[-1]:
                t = arr[-1]['experience'][-1]['date_period'] if('date_period' in arr[-1]['experience'][-1]) else []
                arr[-1]['experience'][-1]['date_period'] = t + regex.findall(row['line'])
        elif row['y_dif'] == 15:
            if 'experience' in arr[-1]:
                t = arr[-1]['experience'][-1]['meta'] if('meta' in arr[-1]['experience'][-1]) else ''
                arr[-1]['experience'][-1]['meta'] = t + ' ' + row['line']
    
    # Parse contact information section
    arr_co = []
    df_co = df_0[df_0['Title'] == 'Contact'].copy() if 'Title' in df_0.columns else pd.DataFrame()
    
    for index, row in df_co.iterrows():
        if row['y_dif'] == 18:
            arr_co.append({})
        
        if row['y_dif'] == 15:
            t = arr_co[-1]['contact'] if ('contact' in arr_co[-1]) else []
            arr_co[-1]['contact'] = t + [row['line']]
    
    return df, df_1, df_0, arr, arr_co