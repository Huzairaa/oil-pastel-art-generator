# Oil Pastel Art Generator

A Python image-processing project that transforms ordinary photographs into oil-pastel-style artwork using simulated brush strokes.

## Features

- Converts photographs into textured, pastel-style paintings.
- Uses multiple brush sizes to build up layers of detail.
- Generates frames showing the painting process.
- Supports exporting the frames to an MP4 video using FFmpeg.

## Requirements

- Python 3.10 or later
- NumPy
- Pillow
- FFmpeg (optional, for video creation)

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

Generate a painting:

```bash
python oil_pastel.py Flowers.jpg
```

Generate painting-process frames:

```bash
python oil_pastel.py Flowers.jpg --video
```

Create a video from the frames (requires FFmpeg):

```bash
ffmpeg -framerate 30 -i frames/%05d.png -pix_fmt yuv420p video.mp4
```

## Output

- `natija.png` — generated painting
- `frames/` — animation frames (optional)
- `video.mp4` — painting-process video (optional)

## Technologies

Python, NumPy, Pillow, FFmpeg

## How it works

The program blurs the source image to estimate local colours, calculates image gradients to guide brush-stroke directions, and draws strokes in progressively smaller sizes to build up the painting effect.
