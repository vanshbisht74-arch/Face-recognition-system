# 🎓 Face Recognition Attendance System   

A professional, real-time attendance management system built with Python, OpenCV, and the `face_recognition` library. Detects and recognizes student faces through a webcam and automatically marks attendance — no manual entry required. 
  
---     
## 📸 Features     
  
| Feature | Description |
|---|---|
| 🎥 Real-time Recognition | Detects and recognizes faces live via webcam |
| 👤 Student Registration | Register students with name + photo upload |
| 📋 Attendance Tracking | Auto-marks attendance once per day per student |
| 🔍 Search & Filter | Search records by student name or date |   
| 📊 Statistics Dashboard | Per-student attendance %, present/absent counts |
| 🚫 Duplicate Prevention | Same student cannot be marked twice in one day |
| 💯 Confidence Score | Shows recognition confidence % on screen |
| 🟩 Color-coded Boxes | Green = recognized, Red = unknown, Yellow = already marked |

---

## 🗂️ Project Structure

```
face_recognition_attendance/
│
├── known_faces/                  ← Student photos (auto-managed)
│   ├── Aman_Sharma.jpg
│   └── Priya_Singh.jpg
│
├── attendance/
│   └── attendance.csv            ← Auto-created attendance log
│
├── database/                     ← Reserved for future use
├── assets/                       ← GUI icons
│
├── main.py                       ← Entry point — run this file
├── gui.py                        ← Full Tkinter dashboard
├── face_recognition_engine.py    ← Webcam + recognition logic
├── attendance_manager.py         ← CSV read/write operations
├── student_registration.py       ← Student photo management
├── statistics.py                 ← Analytics and reporting
├── requirements.txt              ← All dependencies
└── README.md                     ← You are here
```

---

## ⚙️ Installation

### Step 1 — Clone or download the project
```bash
git clone https://github.com/yourusername/face-recognition-attendance.git
cd face-recognition-attendance
```

### Step 2 — Create a virtual environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
# Install cmake first (required to build dlib)
pip install cmake

# Install dlib (face_recognition depends on it)
pip install dlib

# Install all other requirements
pip install -r requirements.txt
```

> ⚠️ **On Windows:** If `dlib` fails to install, download a pre-built wheel from:
> https://github.com/jloh02/dlib/releases
> Then: `pip install dlib-19.24.2-cp310-win_amd64.whl`

### Step 4 — Run the application
```bash
python main.py
```

---

## 🚀 How to Use

### 1. Register a Student
1. Click **"Register Student"**
2. Enter the student's full name
3. Click **"Browse Image"** and select a clear face photo
4. Click **"Register Student"** — photo is saved to `known_faces/`

> 💡 **Tips for best recognition accuracy:**
> - Use a well-lit, front-facing photo
> - One face per photo only
> - Avoid sunglasses or heavy filters

### 2. Start Attendance
1. Click **"Start Attendance"**
2. The webcam opens in a new window
3. Students stand in front of the camera
4. Green box = recognized → attendance marked automatically
5. Yellow box = already marked today
6. Red box = unknown person
7. Press **Q** to stop

### 3. View Attendance Records
1. Click **"View Attendance"**
2. All records shown in a searchable table
3. Search by name or date (format: YYYY-MM-DD)
4. Click column headers to sort

### 4. View Statistics
1. Click **"View Statistics"**
2. See per-student attendance percentage
3. Status labels: Excellent (≥90%) / Good (≥75%) / Average (≥60%) / Poor (≥40%) / Critical (<40%)

---

## 📄 Attendance CSV Format

```csv
Name,Date,Time
Aman Sharma,2024-01-15,09:30:22
Priya Singh,2024-01-15,09:31:05
Rahul Verma,2024-01-16,09:28:47
```

Location: `attendance/attendance.csv`

---

## 🧠 How Face Recognition Works

```
Registration Phase:
  Student Photo → face_recognition → 128-number vector (encoding)
  Saved in memory when app starts

Recognition Phase:
  Webcam Frame → face detected → 128-number vector generated
                                          ↓
                              Compare with all stored vectors
                                          ↓
                              Find closest match (Euclidean distance)
                                          ↓
                    Distance < 0.5?  → Match found → Mark attendance
                    Distance ≥ 0.5?  → "Unknown Person"
```

### Face Distance Thresholds

| Distance | Meaning |
|---|---|
| 0.0 – 0.3 | Very high confidence match |
| 0.3 – 0.5 | Good match (default threshold) |
| 0.5 – 0.6 | Uncertain |
| > 0.6 | Different person |

---

## 🛠️ Configuration

Edit these constants in `face_recognition_engine.py` to tune the system:

```python
RECOGNITION_TOLERANCE      = 0.5   # Lower = stricter matching
RECOGNITION_FRAMES_REQUIRED = 5    # Frames before marking
MARKING_COOLDOWN_SECONDS   = 3     # Seconds between mark attempts
FRAME_SCALE_FACTOR         = 0.5   # 0.5 = process at half resolution
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| Webcam not opening | Check camera connection; try `camera_index=1` |
| Face not detected | Improve lighting; use front-facing photo |
| `dlib` install fails | Install cmake first; use pre-built wheel on Windows |
| `No module named cv2` | Run `pip install opencv-python` |
| GUI looks grey/plain | Install `ttkthemes`: `pip install ttkthemes` |
| Recognition too strict | Increase `RECOGNITION_TOLERANCE` to 0.6 |
| Too many false matches | Decrease `RECOGNITION_TOLERANCE` to 0.4 |
| Image preview blank | Known Tkinter bug — fixed with `self.preview_photo` instance var |

---

## 📦 Dependencies

| Library | Version | Purpose |
|---|---|---|
| `face_recognition` | 1.3.0 | Face detection and encoding |
| `dlib` | 19.24.2 | ML backbone for face_recognition |
| `opencv-python` | 4.8.1.78 | Webcam access and image drawing |
| `numpy` | 1.24.3 | Numerical arrays for encodings |
| `Pillow` | 10.0.0 | Image loading and format conversion |
| `pandas` | 2.0.3 | CSV reading, filtering, analytics |
| `ttkthemes` | 3.2.2 | Modern Tkinter themes |

---

## 🔮 Future Improvements

- [ ] Export attendance to Excel (.xlsx)
- [ ] Email absent student alerts
- [ ] Register via live webcam snapshot
- [ ] SQLite database instead of CSV
- [ ] Multi-camera support
- [ ] Face recognition via CNN model (GPU) for higher accuracy
- [ ] Web dashboard version (Flask/Django)
- [ ] Monthly attendance PDF reports

---

## 👨‍💻 Built With

- **Python 3.8+**
- **OpenCV** — Computer Vision
- **face_recognition** (dlib) — Face Recognition
- **Tkinter** — GUI Framework
- **pandas** — Data Analysis

---

## 📝 License

This project is for educational purposes.
Feel free to use, modify, and build upon it.

---

## 🙏 Acknowledgements

- [ageitgey/face_recognition](https://github.com/ageitgey/face_recognition) — the face recognition library
- [OpenCV](https://opencv.org/) — computer vision framework
- Built as an internship-level learning project for B.Tech CSE students
```
