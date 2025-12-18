# SIIP (Simple Image Interlacement Program)

A simple python CLI tool used to interleave images by rows or columns, intended for use in the creation of structures and weave files for the TC2 Loom.

The goal for the program is to create an new method of constructing multi-weft structures for the TC2. I struggle to comprehend the existing methods of manual construction in Photoshop, and built a tool to construct these in the way my brain can conceptualize them. This is a tool that essentially allows you to add interlacement steps one by one. Examples provided.

This is not intended to be an all in one design tool, or to replace Photoshop! Simply to help with the creation of multi-weft structures (weft backed weaves, supplemental weft structures like overshot/summer & winter). It also has great applications for the creation of doubleweave structures.

## Installation

Best install method is via pip, standalone executables are in development!

<!-- ### Option 1: Standalone Executable (Easiest for Non-Technical Users)

**No Python installation required!**

1. Go to the [Latest Release](../../releases/latest) page
2. Download the executable for your operating system:
   - **macOS (Apple Silicon / M1/M2/M3)**: `image-interlacement` (arm64)
   - **macOS (Intel)**: `image-interlacement` (x86_64)
   - **Linux**: `image-interlacement` (x86_64)
   - **Windows**: `image-interlacement.exe`
3. On macOS/Linux, make it executable and run:
   ```bash
   chmod +x image-interlacement
   ./image-interlacement --help
   ```
4. On Windows, simply double-click or run from Command Prompt:
   ```cmd
   image-interlacement.exe --help
   ``` -->

### Python Package via pip

**Requires Python 3.8 or higher and pip**

Install from PyPI:
```bash
pip install image-interlacement
```

Then run from anywhere:
```bash
image-interlacement --help
```

Or clone and install from source:
```bash
git clone https://github.com/rooomba/image-interlacement
cd image-interlacement-program
pip install -e .
image-interlacement --help
```

<!-- ### Option 3: Run from Source (For Development)

If you're modifying the code:

1. Clone the repository:
```bash
git clone <repository-url>
cd image-interlacement-program
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the program:
```bash
python src/main.py --help
``` -->

## Usage


### Basic Command format:
```bash
image-interlacement composite [image1] [image2] [outputImage] --mode [rows/colums]
```

`image1` and `image2` should be replaced with the filepaths to the structure file images you'd like to use.  

`outputImage` shoudl be replaced with the name/path of where you'd like the composited image to be output.

**Image formats accepted:** `.jpg` `.png` `.bmp` (and more, but these are the only relevant ones to the usecase!)

### Basic Behavior:
The the program will interleave the two provided images (starting from the top left), alternating rows/columns from the source images (starting with `image1`). 

For example: if two images are being interlaced by rows, the program takes row 0 of `image1` for row 0 of `outputImage`, then takes row 0 of `image2` for row 1 of `outputImage`. Row 1 of `image1` becomes row 2 of `outputImage`, row 1 of `image2` becomes row 3, etc etc etc. `outputImage` will be either twice as tall or wide as the original images depending on the interlacement mode!

***Important note on input structure sizes:*** As the program currently operates, if the input images are of two different sizes, it will tile the smaller image to the same size as the larger image. This can cause unexpected issues in structures if you do not take it into account! I would like to eventually add a mode for least common multiple (LCM) tiling, tiling both images so that they had a full repeat that was getting interleaved, be on the lookout for that! For now, just make sure that you are sizing your input structures properly so that they line up on a full repeat.

For example: if your inputs are a 5-end and a 7-end satin, you would want to tile up both images to 35px*35px (35 being the LCM of 5 and 7) so that the program does not attempt to tile the 5-end structure to fit the 7-end structure.

### Additonal tools/options:
**Solid Color instead of image:**
The program by default includes the option to replace either one of the input images with a solid white or black. This is most useful when creating doubleweave structures. Simply replace *either*  of the input images with `white` or `black`, the command will output an error if you replace both.

Example:
```bash
image-interlacement composite image1.png white output.png --mode columns
```

<!-- #### Create a Row-based Composite

Alternate entire rows from two images:

```bash
python src/main.py composite image1.png image2.png output.png --mode rows
```

Pattern: Output rows are interleaved - Row 0 from image1, Row 1 from image2, Row 2 from image1, etc.
The output height will be **2x the input height**.

You can also use solid colors instead of image files:

```bash
python src/main.py composite image1.png white output.png --mode rows
python src/main.py composite image1.png black output.png --mode rows
```

#### Create a Column-based Composite

Alternate entire columns from two images:

```bash
python src/main.py composite image1.png image2.png output.png --mode columns
```

Pattern: Output columns are interleaved - Column 0 from image1, Column 1 from image2, Column 2 from image1, etc.
The output width will be **2x the input width**. -->

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Pillow | >=9.0.0 | Image processing and manipulation |
| NumPy | >=1.21.0 | Efficient array operations for pixel manipulation |


<!-- ### Running the Program

```bash
python src/main.py --help
```

View help for specific commands:

```bash
python src/main.py composite --help
```

## Quick Start

1. **Clone/navigate to repository**:
```bash
git clone https://github.com/rooomba/image-interlacement
cd image-interlacement-program
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Create a composite**:
```bash
python src/main.py composite photo1.jpg photo2.jpg output.jpg --mode rows
``` -->

## Troubleshooting

### Unsupported Image Format
- **Error**: "Cannot identify image file"
- **Solution**: Convert images to PNG, JPG, or BMP format. Use an image converter tool.

## Future additions
- Support for more than 2 images to interleave simultaneously, this is actually required functionality to use the program for anything other than 2 weft weaves. This is first priority.
- Support for stride when it comes to the program, to interleave 2 rows from one image, 1 from another, etc.
- GUI functionality for those less comfortable with a CLI.

## Support

For issues or questions, please open an issue in the repository!

---

**Last Updated**: December 8, 2025  
**Version**: 0.3.5
