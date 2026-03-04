import argparse
import cv2
from datetime import datetime
from loguru import logger
import os
import shutil
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Camera module stream with interval-based image capture.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Directory to save captured imagesimages. Created on demand, if non-existent",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index (default: 0)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        required=True,
        help="Capture interval in seconds",
    )
    parser.add_argument(
        "--rows",
        type=int,
        required=True,
        help="Number of inner checkerboard corners per row",
    )
    parser.add_argument(
        "--cols",
        type=int,
        required=True,
        help="Number of inner checkerboard corners per column",
    )
    return parser.parse_args()


def setup_logging():
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(logs_dir, f"capture_{timestamp}.log")

    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add(log_file_path, level="INFO", rotation="5 MB")

    logger.info(f"Logging initialized")
    logger.info(f"Log file: {log_file_path}")


def prepare_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")
        return

    if os.listdir(path):
        while True:
            choice = input(
                f"Directory '{path}' exists and is not empty.\n"
                "Clear directory? (y/n): "
            ).strip().lower()

            if choice == "y":
                shutil.rmtree(path)
                os.makedirs(path)
                logger.info(f"Cleared directory: {path}")
                break
            elif choice == "n":
                logger.info("User chose not to clear directory. Exiting.")
                sys.exit(0)
            else:
                print("Please enter 'y' or 'n'.")


def main():
    args = parse_args()
    setup_logging()
    prepare_output_directory(args.output)

    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        logger.error("Could not open camera.")
        sys.exit(1)

    capturing = False
    frame_count = 0
    last_capture_time = 0

    checkerboard_size = (args.cols, args.rows)

    logger.info(f"Checkerboard layout (cols, rows): {checkerboard_size}")
    logger.info("Press 's' to start/stop capturing.")
    logger.info("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        found, corners = cv2.findChessboardCorners(
            gray,
            checkerboard_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH \
                + cv2.CALIB_CB_NORMALIZE_IMAGE \
                + cv2.CALIB_CB_FAST_CHECK,
        )

        display_frame = frame.copy()

        if found:
            cv2.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                criteria=(cv2.TERM_CRITERIA_EPS +
                          cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )
            cv2.drawChessboardCorners(display_frame,
                                      checkerboard_size,
                                      corners,
                                      found)

        current_time = time.time()

        if capturing and found and (current_time - last_capture_time >= args.interval):
            filename = f"{frame_count:03d}.png"
            filepath = os.path.join(args.output, filename)
            cv2.imwrite(filepath, frame)
            logger.info(f"Saved {filename}")
            frame_count += 1
            last_capture_time = current_time

        # Overlay information
        status_text = "CAPTURING" if capturing else "IDLE"
        cv2.putText(
            display_frame,
            f"Status: {status_text}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0) if capturing else (0, 0, 255),
            2,
        )

        cv2.putText(
            display_frame,
            f"Saved: {frame_count}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
        )

        cv2.imshow("Checkerboard Capture", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            capturing = not capturing
            state = "STARTED" if capturing else "STOPPED"
            logger.info(f"Capture {state}")
            if capturing:
                last_capture_time = time.time()

        elif key == ord('q'):
            logger.info("Quitting program.")
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("Resources released. Goodbye.")


if __name__ == "__main__":
    main()
