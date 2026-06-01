# ============================================================
# attendance_manager.py
# ============================================================

import csv
import os
import pandas as pd
from datetime import datetime

ATTENDANCE_DIR  = "attendance"
ATTENDANCE_FILE = os.path.join(ATTENDANCE_DIR, "attendance.csv")
CSV_HEADERS     = ["Name", "Date", "Time"]


class AttendanceManager:

    def __init__(self):
        self._ensure_directory_exists()
        self._ensure_file_exists()
        self.marked_today = self._load_todays_records()

    def _ensure_directory_exists(self):
        os.makedirs(ATTENDANCE_DIR, exist_ok=True)

    def _ensure_file_exists(self):
        if not os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, mode='w',
                      newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
            print(f"[INFO] Created attendance file: {ATTENDANCE_FILE}")

    def _get_current_datetime(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    def _load_todays_records(self):
        today, _ = self._get_current_datetime()
        marked = set()
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
            if df.empty:
                return marked
            todays_df = df[df["Date"] == today]
            marked = set(todays_df["Name"].tolist())
        except Exception as e:
            print(f"[WARNING] Could not load today's records: {e}")
        return marked

    def mark_attendance(self, name):
        if name in self.marked_today:
            return False, f"Attendance already marked for {name} today."

        date_str, time_str = self._get_current_datetime()

        try:
            with open(ATTENDANCE_FILE, mode='a',
                      newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([name, date_str, time_str])
            self.marked_today.add(name)
            print(f"[ATTENDANCE] Marked: {name} | {date_str} | {time_str}")
            return True, f"Attendance marked for {name} at {time_str}"
        except Exception as e:
            return False, f"Error marking attendance: {e}"

    def get_all_records(self):
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
            return df
        except Exception as e:
            print(f"[ERROR] Could not read attendance file: {e}")
            return pd.DataFrame(columns=CSV_HEADERS)

    def search_by_name(self, name):
        df = self.get_all_records()
        if df.empty:
            return df
        return df[df["Name"].str.contains(name, case=False, na=False)]

    def search_by_date(self, date_str):
        df = self.get_all_records()
        if df.empty:
            return df
        return df[df["Date"] == date_str]

    def get_statistics(self):
        df = self.get_all_records()
        today, _ = self._get_current_datetime()
        total_students = df["Name"].nunique() if not df.empty else 0
        present_today  = len(self.marked_today)
        attendance_rate = (present_today / total_students * 100
                           if total_students > 0 else 0.0)
        return {
            "total_students"  : total_students,
            "present_today"   : present_today,
            "attendance_rate" : round(attendance_rate, 2),
            "todays_date"     : today
        }

    def is_marked_today(self, name):
        return name in self.marked_today

    def get_todays_attendance(self):
        today, _ = self._get_current_datetime()
        return self.search_by_date(today)


if __name__ == "__main__":
    manager = AttendanceManager()
    print(manager.mark_attendance("Test Student"))
    print(manager.get_statistics())
