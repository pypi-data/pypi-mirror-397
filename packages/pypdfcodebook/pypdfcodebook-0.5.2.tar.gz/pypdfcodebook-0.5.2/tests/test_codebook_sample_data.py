import os
import pandas as pd
import importlib.util
from src.pypdfcodebook.pdfcb_03c_codebook import codebook

def test_codebook_with_sample_data(tmp_path):
    # Paths to sample files
    sample_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
    projectoverview_path = os.path.join(sample_dir, 'pdfcb_00a_projectoverview.md')
    keyterms_path = os.path.join(sample_dir,        'pdfcb_00b_keyterms.md')
    csv_path = os.path.join(sample_dir,             'pdfcb_00c_sampledata.csv')
    datastructure_path = os.path.join(sample_dir,   'pdfcb_00d_data_structure.py')

    # Load CSV
    input_df = pd.read_csv(csv_path)

    # Load data structure dict from .py file
    spec = importlib.util.spec_from_file_location("pdfcb_00d_data_structure", datastructure_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {datastructure_path}")
    ds_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ds_module)
    datastructure = ds_module.DATA_STRUCTURE

    # Set up output in tests directory
    tests_dir = os.path.dirname(__file__)
    output_filename = "test_sample_data"  # Just the name without extension
    
    # Output folder
    output_folder = os.path.abspath("./tests/example_codebooks")
    os.makedirs(output_folder, exist_ok=True)
    output_filename_path = os.path.join(output_folder, f"{output_filename}.pdf")


    # Create codebook
    pdfcodebook = codebook(
        input_df=input_df,
        header_title='Test pyPDFCodebook',
        datastructure=datastructure,
        projectoverview=projectoverview_path,
        keyterms=keyterms_path,
        output_filename=output_filename,
        outputfolder=output_folder
    )
    pdfcodebook.create_codebook()

    # Assert output file was created
    assert os.path.exists(output_filename_path)
