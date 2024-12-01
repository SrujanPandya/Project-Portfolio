# DWT-Based Image Compression and Reconstruction with Feature Extraction

This repository implements a Discrete Wavelet Transform (DWT) pipeline for compressing borehole images captured by sensors and reconstructing them with minimal loss of detail. It also integrates a neural network model to extract critical features from the compressed images, focusing on preserving essential data quality while optimizing storage.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)

---

## Project Overview
Efficient data compression and feature extraction are critical for transmitting high-quality borehole images from drilling sites to the surface. This project addresses these challenges by:
1. Applying **Discrete Wavelet Transform (DWT)** for image compression.
2. Utilizing **Convolutional Neural Networks (CNNs)** for feature extraction.
3. Enabling high-quality reconstruction of images after decompression.

The project uses Haar wavelets for compression and focuses on preserving important features during image reconstruction.

---

## Features
- **Wavelet Transform**: Compresses images into four components (approximation, horizontal, vertical, diagonal).
- **Neural Network Integration**: Extracts critical features from DWT coefficients.
- **Dynamic Data Loading**: Supports direct loading and processing of `.jpg` and `.png` images.
- **Visualization**: Compares original and reconstructed images to evaluate compression quality.
- **Modular Pipeline**: Easily extendable for other image formats or transformations.

---

