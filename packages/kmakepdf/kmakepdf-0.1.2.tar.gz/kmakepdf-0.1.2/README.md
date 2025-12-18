# kmakepdf

**kmakepdf** is a simple yet powerful CLI tool to convert folders containing images and existing PDFs into a single merged PDF file.

## Features

- **Recursive Processing**: Automatically traverse subdirectories to create separate PDFs for each folder.
- **Smart Merging**: Combines both images (`.jpg`, `.jpeg`, `.png`) and existing `.pdf` files.
- **Rich Logging**: Professional, colored console output for better visibility.
- **CLI Interface**: Easy-to-use command line interface.

## Installation

```bash
pip install kmakepdf
```

## Usage

### Basic Usage

Convert a single folder to a PDF:

```bash
kmakepdf /path/to/folder
```

This will create `/path/to/folder.pdf` by default.

### Specify Output File

You can specify a custom output filename:

```bash
kmakepdf /path/to/folder -o my_output.pdf
```

### Recursive Mode

Process all subfolders within a directory:

```bash
kmakepdf /path/to/parent_folder -r
```

This will create a PDF for each subfolder inside `parent_folder`.

## Development

This project uses `uv` for dependency management and `nox` for testing.

### Setup

```bash
# Install dependencies
uv sync
```

### Running Tests

```bash
uv run nox -s tests
```

## License

MIT License. Copyright (c) 2025 Kihoa Nam.
