# Image to PDF

## Overview

**ImageEnhancerPDF** is a powerful tool designed to enhance image readability and generate high-quality PDFs with
precise specifications. Whether you're preparing documents for presentations, reports, or publications, this program
ensures your images are optimally processed and compiled into professional-grade PDFs.

## Features

- **Image Processing**
    - **Enhance Readability**: Automatically adjusts brightness, contrast, and sharpness to make images clearer and more
      legible.
    - **Resize and Crop**: Modify image dimensions to fit specific requirements without compromising quality.
    - **Batch Processing**: Efficiently handle multiple images simultaneously, saving time and effort.

- **PDF Generation**
    - **Custom Specifications**: Create PDFs that meet your desired size, resolution, and formatting standards.
    - **High-Quality Output**: Ensures that the generated PDFs maintain the integrity and quality of the original
      images.
    - **Easy Integration**: Seamlessly combines processed images into a single, well-organized PDF document.

## Installation

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/stable/installation/)

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ImageEnhancerPDF.git
   cd ImageEnhancerPDF
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Enhancing Images and Generating PDF

```bash
python main.py /path/to/images --output_path /path/to/out --resize_ratio 0.8
```

- `input`: Path to the directory containing images to be processed.
- `--output_path`: Desired path for the generated PDF file.
- `--resize_ratio`: (Optional) Factor by which to resize images. Default is 0.5. (e.g., `0.8` reduces size by 20%).

### Example

```bash
python main.py ./images --output ./documents/enhanced_output.pdf --resize 0.75
```

This command processes all images in the `./images` directory, reduces their size by 25%, enhances their readability,
and compiles them into `enhanced_output.pdf` located in the `./documents` folder.

#### Console output

```
Checking 9 images...
100%|██████████| 9/9 [00:00<00:00, 23.02it/s]
Processing 9 images...
100%|██████████| 9/9 [00:03<00:00,  2.55it/s]
Creating PDF file... 9 pages: /User/documents/output.pdf
PDF created successfully with 9 pages: /User/documents/output.pdf

```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any inquiries or support, please contact [juvelop17@gmail.com](mailto:juvelop17@gmail.com).

---

