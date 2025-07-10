import os
import cv2
import numpy as np
import torch
import open_clip
from PIL import Image
from ultralytics import YOLO
from sort.sort import Sort
from torchvision import transforms
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# Setup
device = "cuda" if torch.cuda.is_available() else "cpu"

clip_model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
clip_model = clip_model.to(device)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# Prompts for jersey classification
prompts = [
    "a football player wearing a red Manchester United jersey",
    "a football player wearing a blue Manchester City jersey",
    "a football referee wearing black"
]
text_tokens = tokenizer(prompts).to(device)

TEAM_COLORS = {
    0: ("Red", (0, 0, 255)),     # Team Red (B, G, R)
    1: ("Blue", (255, 0, 0)),    # Team Blue (B, G, R)
    2: ("Referee", (0, 0, 0))    # Referee (B, G, R)
}

# Buffers
player_embeddings = {}
player_data = {}  # Stores {'team_id', 'last_seen'} for each player
player_stats = {} # Stores {'distance', 'last_pos', 'speed'} for each player
prev_positions = {} # Stores the previous center position for speed calculation
ball_possession_time = defaultdict(int) # Tracks possession time per team
frame_index = 0
total_frames = 0

# Ensure 'results' directory exists
if not os.path.exists("results"):
    os.makedirs("results")

# Models and Video Setup
model = YOLO("models/yolo_players.pt") # Ensure this model path is correct
cap = cv2.VideoCapture("videos/15sec_input_720p.mp4") # Ensure this video path is correct

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get video properties for output
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

out = cv2.VideoWriter("results/final_stats_overlay.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
tracker = Sort() # Initialize SORT tracker

# Functions
def jersey_crop(img, x1, y1, x2, y2):
    """
    Crops the jersey region from a player bounding box.
    Assumes jersey is in the upper half of the body.
    """
    h = int(y2 - y1)
    # Ensure crop coordinates are within image bounds
    crop_y1 = int(y1)
    crop_y2 = int(y1 + 0.5 * h)
    crop_x1 = int(x1)
    crop_x2 = int(x2)

    # Handle cases where crop goes out of bounds (shouldn't happen with valid bbox but good practice)
    crop_y1 = max(0, crop_y1)
    crop_y2 = min(img.shape[0], crop_y2)
    crop_x1 = max(0, crop_x1)
    crop_x2 = min(img.shape[1], crop_x2)

    if crop_y2 <= crop_y1 or crop_x2 <= crop_x1:
        return None # Return None if crop region is invalid

    return img[crop_y1:crop_y2, crop_x1:crop_x2]

def get_embedding(img_crop):
    """
    Generates CLIP embedding for the given image crop.
    """
    if img_crop is None or img_crop.shape[0] == 0 or img_crop.shape[1] == 0:
        return None
    image = Image.fromarray(cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB))
    image_input = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        return clip_model.encode_image(image_input).cpu().numpy()

def classify_team(embedding):
    """
    Classifies the team based on the CLIP embedding.
    """
    if embedding is None:
        return None
    with torch.no_grad():
        image_tensor = torch.from_numpy(embedding).to(device)
        text_features = clip_model.encode_text(text_tokens)
        # Normalize features
        image_tensor = image_tensor / image_tensor.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        logits = (image_tensor @ text_features.T).float()
        probs = logits.softmax(dim=-1).cpu().numpy()[0]
        return int(np.argmax(probs))

def calculate_speed(pos1, pos2, fps):
    """
    Calculates speed in km/h and distance moved in meters between two positions.
    Assumes pixel-to-meter conversion is not applied, so distance is in pixels.
    Speed is in km/h assuming a fixed pixel-to-meter ratio (e.g., if 1 pixel = X meters).
    For a more accurate representation, perspective transformation is needed.
    Here, 'dx' is just pixel distance, and 'speed' is relative.
    """
    dx = np.linalg.norm(np.array(pos1) - np.array(pos2))
    # Assuming a simplistic conversion for display; 1 pixel approx 0.05 meters for 720p footage.
    # This value is a rough estimate and should be calibrated for accurate real-world distances.
    pixel_to_meter_ratio = 0.05
    distance_meters = dx * pixel_to_meter_ratio
    
    # Speed in meters per second
    mps = distance_meters / (1/fps) # distance / time_per_frame
    
    # Convert m/s to km/h
    kmph = mps * 3.6
    return kmph, distance_meters

# Main Loop
print("Starting video processing...")
while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        break
    
    frame_index += 1
    total_frames += 1

    # Perform object detection
    results = model(frame, verbose=False) # verbose=False to suppress print output
    detections = []
    ball_coords = None

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])

            if conf < 0.3: # Confidence threshold for detection
                continue
            
            if cls_id in [2, 3]:  # Class IDs for players (adjust if your model has different IDs)
                detections.append([x1, y1, x2, y2, conf])
            elif cls_id == 0:  # Class ID for ball (adjust if your model has different ID)
                ball_coords = ((x1 + x2) // 2, (y1 + y2) // 2)

    # Update SORT tracker with current frame's detections
    dets = np.array(detections) if detections else np.empty((0, 5))
    tracks = tracker.update(dets)

    # Process each tracked object
    for t in tracks:
        x1, y1, x2, y2, track_id = map(int, t)
        center_pos = ((x1 + x2) // 2, (y1 + y2) // 2)

        # If new player (new track_id), classify team and store embedding
        if track_id not in player_data:
            crop = jersey_crop(frame, x1, y1, x2, y2)
            emb = get_embedding(crop)
            if emb is None:
                # If embedding could not be generated, skip this track for now or assign a default/unknown team
                continue
            team_id = classify_team(emb)
            if team_id is None: # If classification failed
                continue
            
            player_embeddings[track_id] = emb
            player_data[track_id] = {'team_id': team_id, 'last_seen': frame_index}
            player_stats[track_id] = {'distance': 0.0, 'last_pos': center_pos, 'speed': 0.0}
        else:
            # Update last seen frame for existing player
            player_data[track_id]['last_seen'] = frame_index

        # Retrieve team ID for the current player
        team_id = player_data[track_id]['team_id']

        # Speed and distance tracking
        if track_id in prev_positions:
            prev = prev_positions[track_id]
            speed, dist = calculate_speed(prev, center_pos, fps)
            player_stats[track_id]['speed'] = speed
            player_stats[track_id]['distance'] += dist
        prev_positions[track_id] = center_pos # Update current position as previous for next frame

        # Ball control tracking
        # Check if player is close to the ball
        if ball_coords and np.linalg.norm(np.array(center_pos) - np.array(ball_coords)) < 50: # 50 pixels radius
            ball_possession_time[team_id] += 1

        # Draw UI elements on the frame
        team_name, color = TEAM_COLORS.get(team_id, ("Unknown", (100, 100, 100))) # Default for unknown team
        label = f"{track_id}"

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Yellow ring at feet (to mark player's base)
        # Ensure y2 is within frame bounds for drawing the circle
        circle_y = min(y2 + 5, frame_height - 1) # Adjust if the circle goes out of bounds
        cv2.circle(frame, (center_pos[0], circle_y), 5, (0, 255, 255), 2)

        # Centered label (track ID)
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = center_pos[0] - text_size[0] // 2
        # Ensure text is drawn within frame bounds
        text_y = max(y1 - 10, text_size[1] + 5) # Avoid drawing above the frame
        cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Speed & distance info
        speed = player_stats[track_id]['speed']
        dist = player_stats[track_id]['distance']
        info = f"{speed:.2f} km/h\n{dist:.2f} m"
        y_offset = 20
        for line in info.split("\n"):
            # Draw text with an outline for better visibility
            cv2.putText(frame, line, (x1, y2 + y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3) # Black outline
            cv2.putText(frame, line, (x1, y2 + y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1) # White text
            y_offset += 15

    # Ball display
    if ball_coords:
        cv2.circle(frame, ball_coords, 6, (0, 255, 255), -1) # Yellow filled circle
        cv2.putText(frame, "Ball", (ball_coords[0] + 5, ball_coords[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2) # Black outline
        cv2.putText(frame, "Ball", (ball_coords[0] + 5, ball_coords[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) # White text

    # Ball control percentage display
    total_control = sum(ball_possession_time.values())
    if total_control == 0: # Avoid division by zero
        total_control = 1e-5 # Small epsilon

    # Draw a background rectangle for better readability
    cv2.rectangle(frame, (10, 10), (320, 80), (255, 255, 255), -1) # White background

    for tid in sorted(TEAM_COLORS.keys()): # Iterate through known team IDs
        if tid == 2: # Skip referee for ball possession stats
            continue
        percent = (ball_possession_time[tid] / total_control) * 100
        team_name, team_color = TEAM_COLORS[tid]
        txt = f"Team {team_name} Control: {percent:.2f}%"
        cv2.putText(frame, txt, (15, 30 + tid * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, team_color, 2)

    # Static camera movement info (as per original code, not implemented actual camera tracking)
    cv2.putText(frame, "Camera Movement X: 0.00", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Camera Movement Y: 0.00", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Write the processed frame to the output video
    out.write(frame)
    # Display the frame
    cv2.imshow("Match Analytics", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

print("Processing complete. Releasing resources.")
cap.release()
out.release()
cv2.destroyAllWindows()