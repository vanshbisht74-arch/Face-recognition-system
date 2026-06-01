# ============================================================
# face_recognition_engine.py  (DeepFace version)
# -- No dlib. No face_recognition library. --
# -- Uses OpenCV for detection, DeepFace for recognition. --
# ============================================================

import cv2
import numpy as np
import os
import time
from deepface import DeepFace

from attendance_manager   import AttendanceManager
from student_registration import StudentRegistration

KNOWN_FACES_DIR          = "known_faces"
RECOGNITION_THRESHOLD    = 0.40   # cosine distance — below = match
RECOGNITION_FRAMES_REQUIRED = 5
MARKING_COOLDOWN_SECONDS = 3
FRAME_SCALE_FACTOR       = 0.5

COLOR_KNOWN       = (0, 220, 0)
COLOR_UNKNOWN     = (0, 0, 220)
COLOR_JUST_MARKED = (0, 215, 255)
COLOR_WHITE       = (255, 255, 255)

FONT       = cv2.FONT_HERSHEY_DUPLEX
FONT_SCALE = 0.6
FONT_THICK = 1


class FaceRecognitionEngine:

    def __init__(self, attendance_manager: AttendanceManager):
        self.attendance_manager = attendance_manager
        self.student_reg        = StudentRegistration()
        self.known_faces        = []   # list of {"name", "image_path"}
        self.frame_counts       = {}
        self.last_marked_time   = {}
        self.is_running         = False
        self.cap                = None
        self.status_callback    = None

        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + \
                       "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.load_known_faces()

    # ── Load students ───────────────────────────────────────

    def load_known_faces(self):
        """
        Stores image paths for all registered students.
        DeepFace compares images directly — no pre-encoding needed.
        """
        self.known_faces = []
        if not os.path.exists(KNOWN_FACES_DIR):
            print("[WARNING] known_faces/ not found.")
            return

        valid_ext = {".jpg", ".jpeg", ".png", ".bmp"}
        files = [f for f in os.listdir(KNOWN_FACES_DIR)
                 if os.path.splitext(f)[1].lower() in valid_ext]

        for filename in files:
            path = os.path.join(KNOWN_FACES_DIR, filename)
            name = os.path.splitext(filename)[0].replace("_", " ")
            self.known_faces.append({"name": name, "image_path": path})
            print(f"  ✓ Loaded: {name}")

        print(f"[ENGINE] {len(self.known_faces)} student(s) loaded.")

    def refresh_known_faces(self):
        print("[ENGINE] Refreshing known faces...")
        self.load_known_faces()

    # ── Recognition ─────────────────────────────────────────

    def _recognize_faces_in_frame(self, frame):
        """
        Step 1 — Detect face locations with Haar Cascade (fast).
        Step 2 — For each face, compare with DeepFace.verify() (accurate).
        """
        results = []

        # Shrink frame for faster Haar detection
        small = cv2.resize(frame, (0, 0),
                           fx=FRAME_SCALE_FACTOR,
                           fy=FRAME_SCALE_FACTOR)
        gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        faces_rect = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )

        if len(faces_rect) == 0:
            return results

        scale = int(1 / FRAME_SCALE_FACTOR)

        for (x, y, w, h) in faces_rect:
            # Scale back to original frame coordinates
            x, y, w, h = x*scale, y*scale, w*scale, h*scale

            # Crop face from original high-quality frame
            face_crop = frame[y:y+h, x:x+w]
            if face_crop.size == 0:
                continue

            name       = "Unknown"
            confidence = 0.0
            is_known   = False

            best_distance = float("inf")
            best_name     = "Unknown"

            for student in self.known_faces:
                try:
                    # DeepFace.verify: compares face_crop vs stored image
                    # Returns {"verified": bool, "distance": float, ...}
                    result = DeepFace.verify(
                        img1_path         = face_crop,
                        img2_path         = student["image_path"],
                        model_name        = "Facenet",
                        distance_metric   = "cosine",
                        enforce_detection = False,
                        silent            = True
                    )
                    distance = result["distance"]
                    if distance < best_distance:
                        best_distance = distance
                        best_name     = student["name"]
                except Exception:
                    continue

            if best_distance <= RECOGNITION_THRESHOLD:
                name       = best_name
                is_known   = True
                confidence = round(
                    (1 - best_distance / RECOGNITION_THRESHOLD) * 100, 1
                )

            # Convert to (top, right, bottom, left) format
            results.append({
                "name"      : name,
                "confidence": confidence,
                "location"  : (y, x+w, y+h, x),
                "is_known"  : is_known
            })

        return results

    # ── Smart attendance marking ────────────────────────────

    def _handle_attendance_marking(self, name):
        if name == "Unknown":
            return False, ""

        current_time = time.time()
        last_time    = self.last_marked_time.get(name, 0)
        if current_time - last_time < MARKING_COOLDOWN_SECONDS:
            return False, ""

        self.frame_counts[name] = self.frame_counts.get(name, 0) + 1
        if self.frame_counts[name] < RECOGNITION_FRAMES_REQUIRED:
            return False, ""

        self.frame_counts[name] = 0
        success, message = self.attendance_manager.mark_attendance(name)
        if success:
            self.last_marked_time[name] = current_time
        return success, message

    # ── Drawing ─────────────────────────────────────────────

    def _draw_face_box(self, frame, result):
        top, right, bottom, left = result["location"]
        name       = result["name"]
        confidence = result["confidence"]
        is_known   = result["is_known"]

        if not is_known:
            color = COLOR_UNKNOWN
        elif self.attendance_manager.is_marked_today(name):
            color = COLOR_JUST_MARKED
        else:
            color = COLOR_KNOWN

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        label = f"{name}  {confidence}%" if is_known else "Unknown Person"
        (tw, th), _ = cv2.getTextSize(label, FONT, FONT_SCALE, FONT_THICK)

        cv2.rectangle(frame,
                      (left, bottom),
                      (left + tw + 10, bottom + th + 10),
                      color, cv2.FILLED)
        cv2.putText(frame, label,
                    (left + 5, bottom + th + 5),
                    FONT, FONT_SCALE, COLOR_WHITE, FONT_THICK)

    def _draw_ui_overlay(self, frame, face_count, status_msg):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (20, 20, 20), cv2.FILLED)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "LIVE",
                    (10, 32), FONT, 0.7, (0, 0, 220), 2)
        cv2.putText(frame, f"Faces: {face_count}",
                    (80, 32), FONT, 0.6, COLOR_WHITE, 1)
        if status_msg:
            cv2.putText(frame, status_msg,
                        (200, 32), FONT, 0.55, (0, 220, 220), 1)
        cv2.putText(frame, "Press 'Q' to quit",
                    (10, h - 10), FONT, 0.5, (180, 180, 180), 1)

    # ── Main webcam loop ────────────────────────────────────

    def start(self, camera_index=0, status_callback=None):
        self.status_callback = status_callback
        self.is_running      = True

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            msg = "ERROR: Could not open webcam."
            print(f"[ENGINE] {msg}")
            if self.status_callback:
                self.status_callback(msg)
            self.is_running = False
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[ENGINE] Webcam started. Press Q to quit.")

        status_msg   = ""
        frame_count  = 0
        face_results = []

        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_count += 1

            # Process every 3rd frame — DeepFace is heavier so
            # we skip more frames to keep video smooth
            if frame_count % 3 == 0:
                face_results = self._recognize_faces_in_frame(frame)
                for result in face_results:
                    if result["is_known"]:
                        marked, msg = self._handle_attendance_marking(
                            result["name"])
                        if marked:
                            status_msg = f"Marked: {result['name']}"
                            print(f"[ENGINE] {status_msg}")
                            if self.status_callback:
                                self.status_callback(status_msg)

            for result in face_results:
                self._draw_face_box(frame, result)
            self._draw_ui_overlay(frame, len(face_results), status_msg)

            cv2.imshow("Face Recognition Attendance System", frame)

            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
                break

        self.stop()

    def stop(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print("[ENGINE] Webcam released.")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    manager = AttendanceManager()
    engine  = FaceRecognitionEngine(manager)
    print("Students:", [s["name"] for s in engine.known_faces])
    if engine.known_faces:
        engine.start()
