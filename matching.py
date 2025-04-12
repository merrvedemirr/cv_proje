#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Matching Module
--------------
Functions for matching job titles using BERT embeddings.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Global variable to cache the BERT model
sbert_model = None

def get_sbert_model():
    """
    Load BERT model and cache it for reuse
    
    Returns:
        SentenceTransformer: The loaded BERT model
    """
    global sbert_model
    if sbert_model is None:
        sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    return sbert_model


def match_all_positions_with_alternate_titles(positions, alternate_titles, top_n=1):
    """
    Match multiple position titles with alternate titles at once using S-BERT embeddings
    
    Args:
        positions: List of position titles to match
        alternate_titles: List of alternate title dictionaries
        top_n: Number of top matches to return for each position (default: 1)
    
    Returns:
        Dictionary mapping each position to its top matching alternate titles with similarity scores
    """
    # Load the S-BERT model
    model = get_sbert_model()
    
    # Get the list of all alternate titles
    all_alt_titles = [item['alternate_title'] for item in alternate_titles]
    
    # Generate embeddings for all positions and alternate titles at once
    position_embeddings = model.encode(positions, show_progress_bar=False)
    title_embeddings = model.encode(all_alt_titles, show_progress_bar=False)
    
    # Calculate cosine similarity matrix (positions x alternate_titles)
    similarities = cosine_similarity(position_embeddings, title_embeddings)
    
    # Create a dictionary to store results for each position
    position_matches = {}
    
    for i, position in enumerate(positions):
        # Get similarity scores for this position
        position_similarities = similarities[i]
        
        # Create a list of (title, similarity) pairs
        title_similarity_pairs = [(alternate_titles[j], position_similarities[j]) for j in range(len(alternate_titles))]
        
        # Sort by similarity (descending)
        title_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Store top N matches for this position
        position_matches[position] = title_similarity_pairs[:top_n]
    
    return position_matches