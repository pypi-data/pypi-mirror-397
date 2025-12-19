
[![PyPI version](https://badge.fury.io/py/pypdfcodebook.svg)](https://badge.fury.io/py/pypdfcodebook)
[![Python](https://img.shields.io/pypi/pyversions/pypdfcodebook.svg)](https://pypi.org/project/pypdfcodebook/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![DOI](https://zenodo.org/badge/1059657046.svg)](https://doi.org/10.5281/zenodo.17956282)

![pyPDFCodebook Logo](.github/images/pdfcb_00a_pypdfcodebooklogo_2025-12-17.png)

# pypdfcodebook

pyPDFCodeBook helps researchers and data professionals create clear, attractive codebooks for tabular datasets. Codebooks document essential metadata—project descriptions, data provenance, variable definitions, and summaries—ensuring your data is understandable and reproducible. While datasets contain values, they rarely explain what each column or row represents. Codebooks fill this gap by providing structured, self-explanatory documentation. They reinforce best practices such as tidy data, unique keys, and transparent variable origins. With pyPDFCodeBook, generating a professional, easy-to-read codebook takes just a few clicks—laying the foundation for good data science and reproducible research. 

**Remember: You are your number one data user, so help your future self out and document your metadata.**

## 🚀 Features

- **Professional PDF Generation**: Create polished, publication-ready codebooks
- **Comprehensive Metadata**: Include project descriptions, data source information, and variable definitions

## 📦 Installation

Install pypdfcodebook from PyPI using pip:

```bash
pip install pypdfcodebook
```

## 🔧 Quick Start

Here's a simple example to get you started:

```python
from pypdfcodebook.pdfcb_03c_codebook import codebook
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv')

# Create a basic codebook (saves to current directory)
cb = codebook(
    input_df=data,
    datastructure={},  # Your data structure dictionary
    projectoverview='',  # Path to markdown file or empty string
    keyterms='',  # Path to markdown file or empty string 
    output_filename='my_codebook'
    # header_title is optional - defaults to "Data Codebook"
    # outputfolder is optional - defaults to current directory
)

# Generate the PDF codebook
cb.create_codebook()
```

## 📖 Usage

### Basic Codebook (Current Directory)

```python
from pypdfcodebook.pdfcb_03c_codebook import codebook

# Minimal setup - output saves to current directory
cb = codebook(
    input_df=your_dataframe,
    datastructure=your_data_structure,
    projectoverview='',
    keyterms='',
    output_filename='your_codebook'
    # header_title defaults to "Data Codebook"
)
cb.create_codebook()
```

### Custom Output Directory

```python
# Specify custom output directory and title
cb = codebook(
    input_df=your_dataframe,
    header_title='Your Project Name',  # Optional: custom title
    datastructure=your_data_structure,
    projectoverview='',
    keyterms='',
    output_filename='your_codebook',
    outputfolder='./custom_output_folder/'
)
cb.create_codebook()
```

### Advanced Configuration

```python
# Full configuration with all options
cb = codebook(
    input_df=your_dataframe,
    header_title='Comprehensive Study',
    datastructure=your_data_structure,
    projectoverview='path/to/overview.md',
    keyterms='path/to/keyterms.md',
    output_filename='comprehensive_codebook',
    outputfolder='./output/',
    footer_image_path='path/to/logo.png'
)
cb.create_codebook()
```

## 📚 Documentation

For comprehensive documentation, examples, and tutorials, visit our [documentation site](https://github.com/nathanael99/pypdfcodebook).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the Mozilla Public License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/nathanael99/pypdfcodebook/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nathanael99/pypdfcodebook/discussions)

## 🏗️ Requirements

- Python 3.9+
- pandas >= 2.2.0
- numpy >= 1.26.0
- fpdf2 >= 2.7.0
- pillow >= 12.0.0
- seaborn >= 0.12.0

