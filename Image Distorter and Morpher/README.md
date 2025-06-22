# Advanced Image Distorter and Morpher

A Python GUI application for creating video effects. This tool can apply procedural distortions (wave, liquid noise) to images/videos and perform feature-based morphing between two images, all through a user-friendly interface.

## Features

- **Dual-Mode UI:** Separate tabs for single-image Distortion and two-image Morphing.
- **Distortion Effects:** Apply animated Wave (Sine/Triangle) or Liquid Noise (Simplex) effects to images or videos.
- **Feature-Based Morphing:** Interactively place control points on two images to generate a smooth morphing animation using Delaunay triangulation.
- **Flexible Output:** Save animations as MP4, WebM, GIF, and WebP.
- **Responsive Processing:** All video generation is threaded to keep the UI from freezing.

## Installation

1.  **Download the script.**
2.  **Install the required libraries:**
    ```bash
    pip install opencv-python numpy scipy Pillow opensimplex imageio imageio-ffmpeg
    ```

## How to Run

Open your terminal and run the script:

```bash
python Image_Distorter_and_Morpher.py
