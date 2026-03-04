# mono_camera_calibration
Calibrate single camera using opencv and checkerboard pattern

## Setup
This code was developed to work on linux. Install Python 3.13+ and [uv](https://docs.astral.sh/uv/). Then, clone this repository and from its source directory run:

```
uv sync
source .venv/bin/activate
```

This will create a virtual environment, install dependencies in it and activate it.

## Calibration process

### Calibration pattern

Print out a checkerboard/chessboard pattern and straighten it out on a flat easily-movable surface (e.g.: a light wooden board, a clipboard). Take note of its number of columns and lines, and the size of the squares. A generator like [this website](https://texflip.altervista.org/calibration-pattern-generator/) may be used to obtain the pattern (you may also simply search for a pdf online).

### Capturing samples

To start the calibration process, ensure the camera is connected and available. The first step is to collect images of the pattern. Use the script `run_image_capture.py` as follows:
