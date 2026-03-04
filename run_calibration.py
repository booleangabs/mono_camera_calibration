import cv2
import numpy as np
import os
import argparse
import sys
from glob import glob
from loguru import logger
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calibrate camera using checkerboard images."
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Directory containing captured checkerboard images")
    parser.add_argument("--rows", type=int, required=True,
                        help="Number of inner corners per column")
    parser.add_argument("--cols", type=int, required=True,
                        help="Number of inner corners per row")
    parser.add_argument("--square_size", type=float, required=True,
                        help="Size of a square (real-world units, e.g., mm)")
    parser.add_argument("--output", type=str, default="camera_params.npz",
                        help="Output .npz file to save calibration parameters")
    return parser.parse_args()


def setup_logging():
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"calibration_{timestamp}.log")

    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add(log_file, level="INFO", rotation="5 MB")
    logger.info("Logging initialized")
    logger.info(f"Log file: {log_file}")


def main():
    args = parse_args()
    setup_logging()

    image_paths = sorted(glob(os.path.join(args.input, "*.png")))
    if not image_paths:
        logger.error("No PNG images found in input directory.")
        sys.exit(1)

    checkerboard_size = (args.cols, args.rows)
    logger.info(f"Checkerboard layout (cols, rows): {checkerboard_size}")
    logger.info(f"Square size: {args.square_size}")

    # Prepare object points
    objp = np.zeros((args.rows * args.cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2)
    objp *= args.square_size

    objpoints = []  # 3D points
    imgpoints = []  # 2D points

    for path in image_paths:
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        found, corners = cv2.findChessboardCorners(
            gray,
            checkerboard_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH +
            cv2.CALIB_CB_NORMALIZE_IMAGE +
            cv2.CALIB_CB_FAST_CHECK
        )

        if found:
            cv2.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                criteria=(cv2.TERM_CRITERIA_EPS +
                          cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )

            objpoints.append(objp)
            imgpoints.append(corners)

            logger.info(f"Checkerboard detected in {os.path.basename(path)}")
        else:
            logger.warning(f"No checkerboard found in {os.path.basename(path)}")

    if len(objpoints) < 3:
        logger.error("Not enough valid checkerboard detections for calibration.")
        sys.exit(1)

    logger.info(f"Running calibration using {len(objpoints)} valid images...")

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        None,
        None
    )

    logger.info(f"Calibration RMS error: {ret}")

    # Save parameters
    np.savez(
        args.output,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        rvecs=rvecs,
        tvecs=tvecs,
        rms=ret
    )

    logger.info(f"Calibration parameters saved to {args.output}")
    logger.info("Done.")


if __name__ == "__main__":
    main()