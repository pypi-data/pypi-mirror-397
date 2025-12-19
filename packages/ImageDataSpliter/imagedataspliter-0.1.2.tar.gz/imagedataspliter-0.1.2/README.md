# DatasetSpliter

A simple Python utility for splitting an image dataset into train, validation, and test subsets while preserving class folder structure.

## Overview

DatasetSpliter provides a function that takes a list of class folders (each containing image files) and splits the dataset into training, validation, and testing subsets. The images are copied into a new output directory while keeping the original class names.

## Resulting directory structure:

output_folder/
├── train/
│ └── class_name/
├── val/
│ └── class_name/
└── test/
└── class_name/


The split process is random but reproducible using a fixed random seed.

## Features

- Supports common image formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`, `.webp`
- Preserves class directory names
- Prints a summary for each class
- Uses only the Python standard library

## Installation

pip install ImageDataSpliter

## Usage

from imagedataspliter import split_dataset

source_folders = [
    "data/cats",
    "data/dogs",
    "data/birds"
]

output_folder = "dataset_split"

split_dataset(
    source_folders=source_folders,
    output_folder=output_folder,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    seed=42
)

## Function Signature

split_dataset(
    source_folders: list[str],
    output_folder: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
)

## Parameters

- source_folders
List of paths to class directories containing images.

- output_folder
Path to the directory where the split dataset will be saved.

- train_ratio
Fraction of images used for training.

- val_ratio
Fraction of images used for validation.

- test_ratio
Fraction of images used for testing.

- seed
Random seed for reproducible splits.

The sum of train_ratio, val_ratio, and test_ratio must equal 1.0.

## Output

- Image files are copied, not moved

- Original data remains unchanged

- Class folder structure is preserved

- Progress information is printed to the console

## Example Output

Processing class: cats
  Total images: 100
  Train: 70, Val: 15, Test: 15

Processing class: dogs
  Total images: 120
  Train: 84, Val: 18, Test: 18

Dataset saved to: dataset_split

## Requirements

Python 3.8 or newer

No external dependencies

## Contributing

Pull requests and issues are welcome. Feel free to suggest improvements or report bugs.