import cv2
import numpy as np
import os
import argparse
import sys
from glob import glob


def parse_args():
    parser = argparse.ArgumentParser(
        description="Undistort images or webcam stream using calibration parameters."
    )
    parser.add_argument("--params", type=str, required=True,
                        help="Path to calibration .npz file")
    parser.add_argument("--input", type=str,
                        help="Path to image or directory (omit for webcam)")
    parser.add_argument("--output", type=str, default="undistorted",
                        help="Output directory")
    parser.add_argument("--crop", action="store_true",
                        help="Crop black borders")
    return parser.parse_args()


def load_params(path):
    data = np.load(path)
    return data["camera_matrix"], data["dist_coeffs"]


def undistort_image(img, camera_matrix, dist_coeffs, crop=False):
    h, w = img.shape[:2]

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (w, h), 1, (w, h)
    )

    dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, newcameramtx)

    if crop:
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

    return dst


def main():
    args = parse_args()

    # Important part 1: loading parameters *****
    camera_matrix, dist_coeffs = load_params(args.params)

    # Webcam mode
    if args.input is None:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Could not open webcam.")
            sys.exit(1)

        print("Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Important part 2: fix distortion *****
            undistorted = undistort_image(
                frame, camera_matrix, dist_coeffs, crop=args.crop
            )

            cv2.imshow("Original", frame)
            cv2.imshow("Undistorted", undistorted)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return

    # Image or directory mode
    if os.path.isfile(args.input):
        os.makedirs(args.output, exist_ok=True)
        img = cv2.imread(args.input)
        # Important part 2: fix distortion *****
        result = undistort_image(
            img, camera_matrix, dist_coeffs, crop=args.crop
        )

        out_path = os.path.join(
            args.output, os.path.basename(args.input)
        )
        cv2.imwrite(out_path, result)
        print(f"Saved: {out_path}")

    elif os.path.isdir(args.input):
        os.makedirs(args.output, exist_ok=True)
        images = glob(os.path.join(args.input, "*.png"))

        for path in images:
            img = cv2.imread(path)
            # Important part 2: fix distortion *****
            result = undistort_image(
                img, camera_matrix, dist_coeffs, crop=args.crop
            )

            out_path = os.path.join(
                args.output, os.path.basename(path)
            )
            cv2.imwrite(out_path, result)
            print(f"Saved: {out_path}")

    else:
        print("Invalid input path.")
        sys.exit(1)


if __name__ == "__main__":
    main()