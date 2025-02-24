import cv2
import numpy as np
import argparse

def create_custom_field(h, w, centers, strength=5):
    y, x = np.mgrid[0:h, 0:w]
    fx = np.zeros((h, w), dtype=np.float32)
    fy = np.zeros((h, w), dtype=np.float32)

    for c in centers:
        dx = x - c['x']
        dy = y - c['y']
        distance = np.sqrt(dx**2 + dy**2) + 1e-5

        if c['type'] == 'curl':
            fx += -strength * dy / distance
            fy += strength * dx / distance
        elif c['type'] == 'div':
            fx += strength * dx / distance
            fy += strength * dy / distance

    return fx, fy

def apply_distortion(frame, fx, fy):
    h, w = frame.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    map_x = (x + fx).astype(np.float32)
    map_y = (y + fy).astype(np.float32)

    distorted = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return distorted

def parse_circle_arg(circle_args):
    centers = []
    for arg in circle_args:
        try:
            effect_type, x, y = arg.split(':')
            if effect_type not in ['curl', 'div']:
                raise ValueError(f"Unknown effect type: {effect_type}")
            centers.append({'type': effect_type, 'x': int(x), 'y': int(y)})
        except Exception as e:
            raise argparse.ArgumentTypeError(f"Invalid circle format '{arg}': {e}")
    return centers

def main(args):
    cap = cv2.VideoCapture(args.input)
    ret, frame = cap.read()
    if not ret:
        print("无法打开输入视频。")
        return
    h, w = frame.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, 30, (w, h))

    while ret:
        fx, fy = create_custom_field(h, w, args.circles, args.alpha)
        distorted = apply_distortion(frame, fx, fy)

        cv2.imshow('Distorted', distorted)
        out.write(distorted)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        ret, frame = cap.read()

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply curl/divergence distortion to video.")
    parser.add_argument('--input', required=True, help="输入视频路径")
    parser.add_argument('--output', default="output.mp4", help="输出视频路径")
    parser.add_argument('--alpha', type=float, default=20, help="扭曲强度")
    parser.add_argument('--circle', dest='circles', type=str, action='append',
                        required=True, help="定义圆圈效果和位置，格式为 effect_type:x:y，例如 curl:300:300 或 div:500:400，可以指定多次")

    args = parser.parse_args()
    args.circles = parse_circle_arg(args.circles)

    main(args)
