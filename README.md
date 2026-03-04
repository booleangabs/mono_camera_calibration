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

```
usage: run_image_capture.py [-h] [--output OUTPUT] [--camera CAMERA] --interval INTERVAL
                            --rows ROWS --cols COLS

Camera module stream with interval-based image capture.

options:
  -h, --help           show this help message and exit
  --output OUTPUT      Directory to save captured imagesimages. Created on demand, if non-existent
  --camera CAMERA      Camera index (default: 0)
  --interval INTERVAL  Capture interval in seconds
  --rows ROWS          Number of inner checkerboard corners per row
  --cols COLS          Number of inner checkerboard corners per column
```

Press "s" to start, stop and resume capture. Press "q" when you are ready to quit. Capture anywhere from 30 to a 100 images while moving the pattern side-to-side, up and down, changing angle and distance. When presenting the pattern to the camera, never turn the pattern anything close to 90° (that is, never come close to swapping row and column order). 

### Finding the camera parameters

To find the extrinsic and intrinsic camera parameters, run `run_calibration.py` as follows:

```
usage: run_calibration.py [-h] --input INPUT --rows ROWS --cols COLS
                          --square_size SQUARE_SIZE [--output OUTPUT]

Calibrate camera using checkerboard images.

options:
  -h, --help            show this help message and exit
  --input INPUT         Directory containing captured checkerboard images
  --rows ROWS           Number of inner corners per column
  --cols COLS           Number of inner corners per row
  --square_size SQUARE_SIZE
                        Size of a square (real-world units, e.g., mm)
  --output OUTPUT       Output .npz file to save calibration parameters
```

This will scan the `input` directory, load images, detect checkerboard, calibrate and save the output parameters to an `npz`.

## Performing undistortion

The script `run_undistortion.py` presents how to use the camera parameters to fix lens distortion. In particular, function `load_params` gives an example on how one could load and extract the relevant parameters and `undistort_image` shows how they can be used to mitigate distortion. The script can be ran as follows:

```
usage: run_undistortion.py [-h] --params PARAMS [--input INPUT] [--output OUTPUT] [--crop]

Undistort images or camera module stream using calibration parameters.

options:
  -h, --help       show this help message and exit
  --params PARAMS  Path to calibration .npz file
  --input INPUT    Path to image or directory (omit for camera module)
  --output OUTPUT  Output directory (omit if camera module is used)
  --crop           Crop black borders
```

Using the `--crop` option is advised.