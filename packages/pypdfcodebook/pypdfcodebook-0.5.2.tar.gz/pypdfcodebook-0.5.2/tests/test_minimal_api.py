#!/usr/bin/env python3
"""
Quick test to demonstrate the new minimal API with optional parameters.
"""

import pandas as pd
from src.pypdfcodebook.pdfcb_03c_codebook import codebook

def test_minimal_api():
    # Sample data
    data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'score': [85, 92, 78]
    }
    df = pd.DataFrame(data)

    # Minimal datastructure
    datastructure = {
        'id': {
            'DataType': 'Int',
            'label': 'Identifier',
            'pyType': 'int',
            'AnalysisUnit': 'Person',
            'MeasureUnit': 'ID',
        },
        'name': {
            'DataType': 'String',
            'label': 'Name',
            'pyType': 'object',
            'AnalysisUnit': 'Person',
            'MeasureUnit': 'Name',
        },
        'score': {
            'DataType': 'Int',
            'label': 'Test Score',
            'pyType': 'int',
            'AnalysisUnit': 'Person',
            'MeasureUnit': 'Score',
        }
    }

    # Test 1: Absolute minimal usage (header_title and outputfolders both optional)
    print("Creating minimal codebook...")
    cb_minimal = codebook(
        input_df=df
    )
    cb_minimal.create_codebook()
    print("✓ Minimal codebook created successfully!")

    # move the codebook to the tests/example_codebooks folder for consistency
    import os
    output_folder = os.path.abspath("./tests/example_codebooks")
    os.makedirs(output_folder, exist_ok=True)
    os.replace("pypdfcodebook.pdf", os.path.join(output_folder, "test_minimal_api.pdf"))
    print("Codebook PDF moved to:", os.path.join(output_folder, "test_minimal_api.pdf"))

if __name__ == "__main__":
    test_minimal_api()