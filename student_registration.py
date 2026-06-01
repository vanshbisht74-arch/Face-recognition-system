# ============================================================
# student_registration.py
# -- Uses OpenCV Haar Cascade for face validation (no dlib) --
# ============================================================

import os
import cv2
import numpy as np
from PIL import Image

KNOWN_FACES_DIR  = "known_faces"
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
MAX_IMAGE_SIZE_MB = 5
SAVE_IMAGE_SIZE   = (400, 400)


class StudentRegistration:

    def __init__(self):
        self._ensure_directory_exists()
        # Load Haar Cascade once — reused for every validation
        cascade_path = cv2.data.haarcascades + \
                       "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def _ensure_directory_exists(self):
        os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

    def _sanitize_name(self, name):
        name = name.strip().title()
        clean = ""
        for char in name:
            if char.isalnum() or char in (" ", "-", "_"):
                clean += char
        return clean.replace(" ", "_")

    def _get_image_path(self, student_name):
        return os.path.join(KNOWN_FACES_DIR, f"{student_name}.jpg")

    def _validate_image_file(self, image_path):
        if not os.path.exists(image_path):
            return False, f"File not found: {image_path}"

        ext = os.path.splitext(image_path)[1].lower()
        if ext not in VALID_EXTENSIONS:
            return False, f"Invalid file type '{ext}'."

        size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if size_mb > MAX_IMAGE_SIZE_MB:
            return False, f"Image too large ({size_mb:.1f}MB). Max: {MAX_IMAGE_SIZE_MB}MB"

        try:
            img = Image.open(image_path)
            img.verify()
        except Exception as e:
            return False, f"Corrupted image file: {e}"

        return True, "Image is valid"

    def _validate_face_in_image(self, image_path):
        """
        Uses OpenCV Haar Cascade to detect faces.
        No dlib or face_recognition needed.
        """
        try:
            img  = cv2.imread(image_path)
            if img is None:
                return False, "Could not read image file."

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(40, 40)
            )

            if len(faces) == 0:
                return False, ("No face detected. "
                               "Please use a clear, front-facing photo.")
            if len(faces) > 1:
                return False, (f"{len(faces)} faces detected. "
                               "Please use a photo with ONE person only.")

            return True, "Face detected successfully"

        except Exception as e:
            return False, f"Error analyzing image: {e}"

    def _process_and_save_image(self, source_path, destination_path):
        try:
            img = Image.open(source_path)
            img = img.convert("RGB")
            img = img.resize(SAVE_IMAGE_SIZE, Image.LANCZOS)
            img.save(destination_path, "JPEG", quality=95)
            return True, f"Image saved to {destination_path}"
        except Exception as e:
            return False, f"Failed to save image: {e}"

    def register_student(self, name, image_path):
        clean_name = self._sanitize_name(name)
        if not clean_name:
            return False, "Invalid name."

        if self.student_exists(clean_name):
            return False, f"Student '{clean_name}' is already registered."

        is_valid, msg = self._validate_image_file(image_path)
        if not is_valid:
            return False, msg

        has_face, msg = self._validate_face_in_image(image_path)
        if not has_face:
            return False, msg

        destination = self._get_image_path(clean_name)
        saved, msg  = self._process_and_save_image(image_path, destination)
        if not saved:
            return False, msg

        print(f"[REGISTRATION] Registered: {clean_name}")
        return True, f"Student '{clean_name}' registered successfully!"

    def student_exists(self, name):
        clean_name = self._sanitize_name(name)
        return os.path.exists(self._get_image_path(clean_name))

    def get_all_students(self):
        students = []
        try:
            for filename in os.listdir(KNOWN_FACES_DIR):
                ext = os.path.splitext(filename)[1].lower()
                if ext in VALID_EXTENSIONS:
                    name = os.path.splitext(filename)[0].replace("_", " ")
                    students.append(name)
        except Exception as e:
            print(f"[ERROR] Could not list students: {e}")
        return sorted(students)

    def get_student_count(self):
        return len(self.get_all_students())

    def delete_student(self, name):
        clean_name = self._sanitize_name(name)
        path = self._get_image_path(clean_name)
        if not os.path.exists(path):
            return False, f"Student '{clean_name}' not found."
        try:
            os.remove(path)
            return True, f"Student '{clean_name}' deleted."
        except Exception as e:
            return False, f"Could not delete: {e}"

    def get_student_image_path(self, name):
        clean_name = self._sanitize_name(name)
        path = self._get_image_path(clean_name)
        return path if os.path.exists(path) else None


if __name__ == "__main__":
    reg = StudentRegistration()
    print("Registered students:", reg.get_all_students())
