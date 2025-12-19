#!/usr/bin/env python3
"""
Test auto-generation of data structure when none is provided.
"""

import pandas as pd
from src.pypdfcodebook.pdfcb_03c_codebook import codebook
import os

def test_auto_generated_datastructure():
    """Test that pypdfcodebook can auto-generate a data structure."""
    
    # Sample data with various data types
    data = {
        'person_id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Edward'],
        'age': [25, 30, 22, 40, 35],
        'salary': [50000.50, 65000.75, 45000.00, 80000.25, 72000.00],
        'department': ['HR', 'IT', 'Finance', 'IT', 'HR'],
        'is_manager': [False, True, False, True, False],
        'satisfaction': [4, 5, 3, 4, 5]  # Looks categorical (ordinal)
    }
    df = pd.DataFrame(data)

    print("Testing auto-generation of data structure...")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {list(df.columns)}")
    print(f"DataFrame dtypes:\n{df.dtypes}")

    # Create codebook WITHOUT providing a datastructure - should auto-generate
    cb = codebook(
        input_df=df,
        header_title="Auto-Generated Structure Test",
        # datastructure={},  # Commented out - let it auto-generate
        projectoverview="",
        keyterms="",
        output_filename="test_auto_generated_structure"
    )
    
    print("\nGenerated data structure:")
    for var_name, var_info in cb.datastructure.items():
        print(f"\n{var_name}:")
        for key, value in var_info.items():
            print(f"  {key}: {value}")
    
    # Test that the structure was auto-generated
    assert cb._auto_generated_structure == True
    assert len(cb.datastructure) == len(df.columns)
    
    # Test some expected mappings (no categorical detection)
    assert cb.datastructure['person_id']['DataType'] == 'Int'
    assert cb.datastructure['person_id']['pyType'] == 'int'
    assert cb.datastructure['name']['DataType'] == 'String'
    assert cb.datastructure['name']['pyType'] == 'object'
    assert cb.datastructure['salary']['DataType'] == 'Float'
    assert cb.datastructure['salary']['pyType'] == 'float'
    assert cb.datastructure['department']['DataType'] == 'String'
    assert cb.datastructure['department']['pyType'] == 'object'
    assert cb.datastructure['satisfaction']['DataType'] == 'Int'
    assert cb.datastructure['satisfaction']['pyType'] == 'int'
    assert cb.datastructure['is_manager']['DataType'] == 'String'
    assert cb.datastructure['is_manager']['pyType'] == 'object'
    
    # Generate the codebook to ensure it works end-to-end
    cb.create_codebook()
    
    # Check that PDF was created
    expected_path = os.path.join(os.getcwd(), "test_auto_generated_structure.pdf")
    assert os.path.exists(expected_path), f"PDF not created at {expected_path}"
    
    print(f"\n✅ Success! Codebook with auto-generated structure created at: {expected_path}")
    print("📋 The PDF should include a note about the auto-generated structure.")

    # move the codebook to the tests/example_codebooks folder for consistency
    output_folder = os.path.abspath("./tests/example_codebooks")
    os.makedirs(output_folder, exist_ok=True)
    os.replace("test_auto_generated_structure.pdf", os.path.join(output_folder, "test_auto_generated_structure.pdf"))
    print("Codebook PDF moved to:", os.path.join(output_folder, "test_auto_generated_structure.pdf"))

if __name__ == "__main__":
    test_auto_generated_datastructure()
    print("\n🎉 All auto-generation tests passed!")