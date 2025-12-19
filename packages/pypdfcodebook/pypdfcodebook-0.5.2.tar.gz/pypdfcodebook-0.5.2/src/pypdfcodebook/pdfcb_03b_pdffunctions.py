"""
******************************************************************************
* Project: pypdfcodebook                                                     *
* License: BSD 3-Clause License                                              *
* Author/Maintainer: Nathanael Rosenheim                                     *
* Copyright (c) 2025 Nathanael Rosenheim                                     *
******************************************************************************

Code originally developed by Nathanael Rosenheim
Updates after December 2025 made with assistance from Claude Sonnet 4 LLM
in VS Code Agent Mode.

Date Last Modified: December 17, 2025
"""

import csv
import os
from fpdf import FPDF, XPos, YPos
from typing import List, Union, Any, Optional, Tuple
from PIL import Image

"""
Help to make Codebook PDF
https://pyfpdf.github.io/fpdf2/Tutorial.html#tuto-5-creating-tables
https://github.com/bvalgard/create-pdf-with-python-fpdf2

# Code for fpdf
https://github.com/PyFPDF/fpdf2/blob/master/fpdf/fpdf.py
# Docs for fpdf
https://pyfpdf.github.io/fpdf2/index.html

RGB color codes
https://www.rapidtables.com/web/color/RGB_Color.html

Possible alternative to fpdf
https://github.com/jorisschellekens/borb
"""

# Header is a FPDF2 function that is called with addpage
class PDF(FPDF):
    def __init__(self,
        header_text: str = "Header Text",
        footer_text: str = "Footer Text",
        footer_image_path: str = ""):
        """
        Initialize a PDF document with custom header and footer text.

        Args:
            header_text (str): Text to display in the header.
            footer_text (str): Text to display in the footer.
            footer_image_path (str): Path to an image file to display in the footer.
                If empty string, uses default pypdfcodebook logo. To disable footer image
                entirely, pass None. The file must exist and be in a supported format 
                (PNG, JPG, JPEG, BMP, GIF, TIF, TIFF). If file is missing/unsupported,
                no image will be displayed.
        """
        # Help with understating super().__init__()
        # https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        # Super is a function that calls the parent class
        # Need to set the page format here
        super().__init__(orientation = "P", unit = "mm", format = "letter")
        self.header_text = header_text
        self.footer_text = footer_text
        
        # Use default logo if no image path provided
        if footer_image_path == "":
            # Get the directory where this script is located
            current_dir = os.path.dirname(__file__)
            default_logo = os.path.join(current_dir, "pdfcb_00a_pypdfcodebooklogo_2025-12-17.png")
            self.footer_image_path = default_logo if os.path.exists(default_logo) else ""
        elif footer_image_path is None:
            # Explicitly disable footer image
            self.footer_image_path = ""
        else:
            # Use provided path
            self.footer_image_path = footer_image_path
        
    def calculate_footer_image_size(self, image_path: str, max_height: float = 15.0) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate appropriate width and height for footer image to fit within constraints.
        
        This function determines the optimal size for a footer image by:
        1. Getting the actual image dimensions
        2. Calculating scaling factor to fit within max height and page width
        3. Maintaining the original aspect ratio
        
        Args:
            image_path (str): Path to the image file
            max_height (float): Maximum height in mm for the footer image. Defaults to 15.0mm.
            
        Returns:
            Tuple[Optional[float], Optional[float]]: (width, height) in mm, or (None, None) if error
            
        Note:
            - Returns (None, None) if image cannot be processed
            - Image is scaled proportionally to maintain aspect ratio
            - Will not exceed max_height or effective page width (self.epw)
        """
        try:
            # Open image and get dimensions
            with Image.open(image_path) as img:
                img_width_px, img_height_px = img.size
                
            # Convert pixels to mm (assuming 96 DPI)
            # 1 inch = 25.4 mm, so 1 pixel = 25.4/96 mm
            px_to_mm = 25.4 / 96
            img_width_mm = img_width_px * px_to_mm
            img_height_mm = img_height_px * px_to_mm
            
            # Calculate scaling factors for both dimensions
            width_scale = self.epw / img_width_mm
            height_scale = max_height / img_height_mm
            
            # Use the smaller scale factor to ensure image fits in both dimensions
            scale_factor = min(width_scale, height_scale, 1.0)  # Don't scale up
            
            # Calculate final dimensions
            final_width = img_width_mm * scale_factor
            final_height = img_height_mm * scale_factor
            
            return final_width, final_height
            
        except Exception as e:
            print(f"Warning: Could not calculate image dimensions for {image_path}: {str(e)}")
            return None, None
        
    def header(self) -> None:
        """
        Create the header for each PDF page.
        
        This method is automatically called by FPDF2 when a new page is added.
        It sets up the header with custom text that was provided during PDF initialization.
        The header uses Helvetica Bold 15pt font and is centered on the page.
        
        Returns:
            None: This method modifies the PDF document in-place.
        """
        # Setting font: helvetica bold 15
        self.set_font("helvetica", "B", 15)
        # Moving cursor to the right:
        self.cell(w = 80)
        #pdf.set_y(-10)
        # Printing title:
        self.cell(w = 30, 
                  h = 10, 
                  text = self.header_text, 
                  border = 0,
                  new_x = XPos.RIGHT,
                  new_y = YPos.TOP,
                  align = "C")
        # Performing a line break:
        self.ln(15)

    # Footer is a FPDF2 function that is called with addpage
    def footer(self) -> None:
        """
        Create the footer for each PDF page.
        
        This method is automatically called by FPDF2 when a new page is added.
        The footer includes:
        - An optional image (if footer_image_path was provided during initialization)
        - Page numbering in format "Page X/{nb}" where {nb} is total pages
        - Custom footer text (provided during initialization)
        
        The footer uses Helvetica Italic 8pt font and is centered on the page.
        
        Returns:
            None: This method modifies the PDF document in-place.
        """
        # Position cursor for footer content
        self.set_y(self.eph-10)
        
        # Add image if available and valid
        if self.footer_image_path and os.path.exists(str(self.footer_image_path)):
            try:
                # Calculate appropriate image size
                img_width, img_height = self.calculate_footer_image_size(str(self.footer_image_path))
                
                if img_width and img_height:
                    # Position image at left margin
                    x_position = 15  # Left margin
                    # Position image at bottom of page with some margin
                    y_position = self.h - img_height - 5  # 5mm margin from bottom
                    
                    self.image(name=str(self.footer_image_path), 
                             w=img_width, 
                             h=img_height,
                             x=x_position, 
                             y=y_position)
                else:
                    print(f"Warning: Could not determine size for image {self.footer_image_path}")
                    
            except Exception as e:
                print(f"Warning: Could not render image {self.footer_image_path}: {str(e)}")

        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.ln(23)
        self.cell(w = 0, h = 10, 
                    text = f"Page {self.page_no()}/{{nb}}",
                    border = 0,
                    new_x = XPos.LEFT,
                    new_y = YPos.NEXT,
                    align = "C")
        self.cell(w = 0, h = 0,
                    text = self.footer_text, 
                    border = 0,
                    new_x = XPos.LEFT,
                    new_y = YPos.TOP,
                    align = "C")

    ## TABLE FUNCTIONS
    # Code from: https://github.com/bvalgard/create-pdf-with-python-fpdf2/blob/master/table_function.py

    def get_col_widths(self, 
                      cell_width: Union[str, int, List[int]], 
                      data: List[List[str]], 
                      table_data: List[List[str]]) -> Any:
        """
        Calculate column widths for table creation based on the specified method.
        
        This function supports different strategies for determining column widths:
        - 'even': Distribute available width evenly across all columns
        - 'uneven': Calculate widths based on content length (auto-fit)
        - 'split-20-80': Create a two-column layout with 20%/80% width split
        - int: Use a fixed width for all columns (passthrough)
        - List[int]: Specify individual width for each column (passthrough)
        
        Args:
            cell_width (Union[str, int, List[int]]): Width calculation method or specific values.
                - str: 'even', 'uneven', or 'split-20-80'
                - int: Fixed width for all columns
                - List[int]: Individual width for each column
            data (List[List[str]]): Table data excluding headers.
            table_data (List[List[str]]): Complete table data including headers.
        
        Returns:
            Union[float, int, List[int], List[float]]: Column width(s) based on input method.
                - float: When cell_width is 'even'
                - List[float]: When cell_width is 'uneven'
                - List[int]: When cell_width is 'split-20-80' or List[int]
                - int: When cell_width is int
        
        Note:
            - For 'uneven' mode, adds 4mm padding to each calculated width
            - Uses self.epw (effective page width) for percentage calculations
            - Content length is measured using self.get_string_width()
        """
        col_width = cell_width
        if col_width == 'even':
            col_width = self.epw / len(data[0]) - 1  
            # distribute content evenly   
            # epw = effective page width (width of page not including margins)
        elif col_width == 'uneven':
            col_widths = []
            # searching through columns for largest sized cell (not rows but cols)
            for col in range(len(table_data[0])): # for every row
                longest = 0 
                for row in range(len(table_data)):
                    cell_value = str(table_data[row][col])
                    value_length = self.get_string_width(cell_value)
                    if value_length > longest:
                        longest = value_length
                col_widths.append(longest + 4) # add 4 for padding
            col_width = col_widths

        # Add new option for a 20% 80% split
        elif col_width == 'split-20-80':
            col_80width = int(self.epw * 0.8)
            col_20width = int(self.epw - col_80width)
            col_width = [col_20width, col_80width]

        return col_width

    def create_table(self,
                    table_data: List[List[str]], 
                    title: str = '', 
                    data_size: int = 10, 
                    title_size: int = 12, 
                    align_data: str = 'L', 
                    align_header: str = 'L', 
                    cell_width: Union[str, int, List[int]] = 'uneven',
                    line_space: float = 2.5) -> None:
        """
        Create a formatted table in the PDF document.
        
        This method creates a professional-looking table with headers, data rows,
        and optional title. It supports various alignment options, font sizes,
        and column width strategies.
        
        Code adapted from: https://github.com/bvalgard/create-pdf-with-python-fpdf2/blob/main/table_function.py
        
        Args:
            table_data (List[List[str]]): List of lists with first element being list of headers.
            title (str, optional): Title of the table. Defaults to ''.
            data_size (int, optional): Font size of table data. Defaults to 10.
            title_size (int, optional): Font size of the table title. Defaults to 12.
            align_data (str, optional): Alignment for table data. Defaults to 'L'.
                - 'L': Left align
                - 'C': Center align  
                - 'R': Right align
            align_header (str, optional): Alignment for table headers. Defaults to 'L'.
                - 'L': Left align
                - 'C': Center align
                - 'R': Right align
            cell_width (Union[str, int, List[int]], optional): Column width strategy. Defaults to 'uneven'.
                - 'even': Evenly distribute cell/column width
                - 'uneven': Base cell size on length of cell/column items
                - 'split-20-80': Create 20%/80% two-column split
                - int: Fixed width for all cells/columns
                - List[int]: Individual width for each column
            line_space (float, optional): Spacing between rows in table. Defaults to 2.5.
        
        Returns:
            None: This method modifies the PDF document in-place.
            
        Note:
            - Headers are automatically formatted with lines above and below
            - Data rows alternate with light blue background fill
            - Table automatically handles text wrapping within cells
        """

        self.set_font("helvetica", size=title_size)
        line_height = self.font_size * line_space

        # Set table data and headers
        header = table_data[0]
        data = table_data[1:]

        # Get column widths
        col_width = self.get_col_widths(
                                cell_width=cell_width, 
                                data=data, 
                                table_data=table_data)

        # TABLE CREATION #
        # add title
        #print(title)
        if title != '':
            self.multi_cell(0, line_height, title, 
                    border=0, align='j')
            self.ln(line_height) # move cursor back to the left margin
        
        self.set_font("helvetica",size=data_size)
        # add header
        y1 = self.get_y()
        x_left = self.get_x()
        x_right = self.epw + x_left

        # Add header row
        for i in range(len(header)):
            datum = header[i]
            # Handle both single width and list of widths
            if isinstance(col_width, list):
                width = col_width[i]
            else:
                width = col_width
            self.multi_cell(width, line_height, 
                text=datum, border=0, 
                align=align_header, new_x="RIGHT", new_y="TOP", 
                max_line_height=self.font_size)
        x_right = self.get_x()
        self.ln(line_height) # move cursor back to the left margin
        y2 = self.get_y()
        # Add lines around headers
        self.line(x_left,y1,x_right,y1)
        self.line(x_left,y2,x_right,y2)

        # Add Data
        self.set_fill_color(224, 235, 255)
        fill = False
        # loop over rows
        for row in data:
            for j in range(len(row)):
                datum = row[j]
                if not isinstance(datum, str):
                    datum = str(datum)
                # Handle both single width and list of widths
                if isinstance(col_width, list):
                    adjusted_col_width = col_width[j]
                else:
                    adjusted_col_width = col_width
                self.multi_cell(adjusted_col_width, 
                    line_height, text=datum, 
                    border=0, align=align_data, new_x="RIGHT", new_y="TOP",
                    max_line_height=self.font_size* line_space,
                    fill = fill)
            fill = not fill
            self.ln(self.font_size * line_space) # move cursor back to the left margin
        # Add line to bottom of table
        y3 = self.get_y()+1
        self.line(x_left,y3,x_right,y3)
