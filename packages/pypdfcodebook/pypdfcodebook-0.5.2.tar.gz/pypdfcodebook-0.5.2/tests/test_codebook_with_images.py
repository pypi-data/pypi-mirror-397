import os
import pandas as pd
import importlib.util
from src.pypdfcodebook.pdfcb_03c_codebook import codebook
from src.pypdfcodebook.pdfcb_03b_pdffunctions import PDF


def test_codebook_with_images(tmp_path):
    # Paths to sample files
    sample_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
    projectoverview_path = os.path.join(sample_dir, 'pdfcb_00a_projectoverview.md')
    keyterms_path = os.path.join(sample_dir,        'pdfcb_00b_keyterms.md')
    csv_path = os.path.join(sample_dir,             'pdfcb_00c_sampledata.csv')
    datastructure_path = os.path.join(sample_dir,   'pdfcb_00d_data_structure.py')
    footer_image_path = os.path.join(sample_dir, 'pdfcb_00e_samplelogo.png')
    
    # Define figure list - users can easily modify this list
    figure_filenames = [
        'pdfcb_00f_satisfaction_dist.png',  # Satisfaction histogram
        'pdfcb_00g_age_dist.png',  # Age distribution
        'pdfcb_00h_region_dist.png'  # Regional pie charts
    ]
    
    # Convert filenames to full paths
    figure_list_paths = [os.path.join(sample_dir, filename) for filename in figure_filenames]

    # Check if paths exist, else set to empty string or None
    projectoverview_path = projectoverview_path if os.path.exists(projectoverview_path) else ""
    keyterms_path = keyterms_path if os.path.exists(keyterms_path) else ""
    csv_path = csv_path if os.path.exists(csv_path) else ""
    datastructure_path = datastructure_path if os.path.exists(datastructure_path) else ""
    footer_image_path = footer_image_path if os.path.exists(footer_image_path) else ""
    # Keep figure_list_paths as is - individual validation happens later

    # Load CSV
    input_df = pd.read_csv(csv_path)

    # Load data structure dict from .py file
    spec = importlib.util.spec_from_file_location("pdfcb_00d_data_structure", datastructure_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {datastructure_path}")
    ds_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ds_module)
    datastructure = ds_module.DATA_STRUCTURE


    # Output folder
    output_filename = "test_codebook_with_images"
    output_folder = os.path.abspath("./tests/example_codebooks")
    os.makedirs(output_folder, exist_ok=True)
    output_filename_path = os.path.join(output_folder, f"{output_filename}.pdf")

    # Validate image formats and process figure list
    supported_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff'}
    
    # Validate footer image
    if footer_image_path != "":
        footer_ext = os.path.splitext(footer_image_path)[1].lower()
        print(f"Footer image extension: {footer_ext}")
        footer_image_path_to_use = footer_image_path if footer_ext in supported_exts else ""
        if not footer_image_path_to_use:
            print(f"Skipping unsupported footer image format: {footer_image_path}")
    else:
        footer_image_path_to_use = ""
    
    # Process figure list paths
    figures_to_use = []
    if figure_list_paths:
        for figure_path in figure_list_paths:
            if figure_path and os.path.exists(figure_path):
                figure_ext = os.path.splitext(figure_path)[1].lower()
                if figure_ext in supported_exts:
                    figures_to_use.append(figure_path)
                    print(f"Added figure: {os.path.basename(figure_path)}")
                else:
                    print(f"Skipping unsupported figure format: {os.path.basename(figure_path)}")
            elif figure_path:
                print(f"Figure not found: {figure_path}")

    print(f"\nUsing footer image: {os.path.basename(footer_image_path_to_use) if footer_image_path_to_use else 'None'}")
    print(f"Total figures to include: {len(figures_to_use)}")
    if figures_to_use:
        print("Figure list:")
        for i, fig in enumerate(figures_to_use, 1):
            print(f"  {i}. {os.path.basename(fig)}")
    print()

    # Pass figures as a list if valid, else None
    figures_param = figures_to_use if figures_to_use else None
    pdfcodebook = codebook(
        input_df=input_df,
        header_title='Regional Satisfaction Survey Codebook',
        datastructure=datastructure,
        projectoverview=projectoverview_path,
        keyterms=keyterms_path,
        output_filename=output_filename,
        outputfolder=output_folder,
        figures=figures_param,
        footer_image_path=footer_image_path_to_use
    )
    pdfcodebook.create_codebook()

    # Assert output file was created
    assert os.path.exists(output_filename_path)
