import os
import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("models/yolo_players.pt")

# Load video
cap = cv2.VideoCapture("videos/15sec_input_720p.mp4")

# Output folder
save_dir = "players_dataset"
os.makedirs(save_dir, exist_ok=True)

# State tracking
frame_idx = 0
frame = None
display_frame = None
current_detections = []
selected_box = None
label_map = {}  # {(frame_idx, box_idx): 'pX'}

def detect_players(f):
    results = model(f, verbose=False)[0]
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        if conf > 0.3 and cls_id in [2, 3]:  # player class IDs
            detections.append((x1, y1, x2, y2))
    return detections

def draw_detections():
    global display_frame
    display_frame = frame.copy()
    for i, (x1, y1, x2, y2) in enumerate(current_detections):
        if selected_box == i:
            color = (0, 0, 255)  # red for selected
        else:
            color = (0, 255, 0) if (frame_idx, i) in label_map else (0, 255, 255)
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        label = label_map.get((frame_idx, i))
        if label:
            cv2.putText(display_frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def mouse_callback(event, x, y, flags, param):
    global selected_box
    if event == cv2.EVENT_LBUTTONDOWN:
        for i, (x1, y1, x2, y2) in enumerate(current_detections):
            if x1 <= x <= x <= x2 and y1 <= y <= y <= y2:
                selected_box = i
                print(f"[INFO] Box {i} selected at frame {frame_idx}")
                draw_detections()  # redraw with highlight
                break

cv2.namedWindow("Player Labeling")
cv2.setMouseCallback("Player Labeling", mouse_callback)

print("\n✅ INSTRUCTIONS:")
print(" - Press 'n' to go to next frame.")
print(" - Click a player box to select it.")
print(" - Press a key (0–9, a–z, A–Z) to assign label.")
print(" - Press 'q' to quit.\n")

# Load the first frame
ret, frame = cap.read()
if not ret:
    print("❌ Could not read the first frame.")
    cap.release()
    exit()

current_detections = detect_players(frame)
draw_detections()
frame_idx += 1

while True:
    if display_frame is not None:
        cv2.imshow("Player Labeling", display_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    # Load next frame on 'n'
    if key == ord('n'):
        ret, frame = cap.read()
        if not ret:
            print("✅ End of video.")
            break
        selected_box = None
        current_detections = detect_players(frame)
        draw_detections()
        frame_idx += 1

    # Handle labeling
    if selected_box is not None:
        if (ord('0') <= key <= ord('9') or
            ord('a') <= key <= ord('z') or
            ord('A') <= key <= ord('Z')):

            label_char = chr(key).upper()
            label = f"p{label_char}"
            box_key = (frame_idx, selected_box)

            # Avoid duplicate labels in same frame
            existing_labels = [v for (f, _), v in label_map.items() if f == frame_idx]
            if label in existing_labels:
                print(f"⚠️ Label '{label}' already used in this frame.")
                selected_box = None
                draw_detections()
                continue

            label_map[box_key] = label

            x1, y1, x2, y2 = current_detections[selected_box]
            crop = frame[y1:y2, x1:x2]
            if crop.size != 0:
                filename = f"{label}_f{frame_idx}.jpg"
                path = os.path.join(save_dir, filename)
                cv2.imwrite(path, crop)
                print(f"✅ Label '{label}' assigned to box {selected_box} at frame {frame_idx} — saved {filename}")

            selected_box = None
            draw_detections()

cap.release()
cv2.destroyAllWindows()
