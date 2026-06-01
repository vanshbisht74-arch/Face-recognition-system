# ============================================================
# statistics.py
# ============================================================

import pandas as pd
import os
from datetime import datetime, timedelta

from attendance_manager   import AttendanceManager
from student_registration import StudentRegistration


class AttendanceStatistics:

    def __init__(self, attendance_manager: AttendanceManager,
                 student_registration: StudentRegistration):
        self.att_manager = attendance_manager
        self.stu_reg     = student_registration

    def _get_today_str(self):
        return datetime.now().strftime("%Y-%m-%d")

    def _safe_percentage(self, part, total):
        if total == 0:
            return 0.0
        return round((part / total) * 100, 1)

    def _get_clean_dataframe(self):
        df = self.att_manager.get_all_records()
        if df.empty:
            return df
        df = df.dropna(subset=["Name", "Date"])
        df = df.drop_duplicates(subset=["Name", "Date"], keep="first")
        df["Date"] = df["Date"].astype(str)
        return df

    def get_today_summary(self):
        today        = self._get_today_str()
        all_students = self.stu_reg.get_all_students()
        todays_df    = self.att_manager.get_todays_attendance()

        present_names = todays_df["Name"].tolist() if not todays_df.empty else []
        present_set   = set(present_names)
        absent_names  = [s for s in all_students if s not in present_set]

        total_registered = len(all_students)
        present_today    = len(present_names)
        absent_today     = len(absent_names)

        return {
            "date"            : today,
            "total_registered": total_registered,
            "present_today"   : present_today,
            "absent_today"    : absent_today,
            "attendance_pct"  : self._safe_percentage(present_today,
                                                       total_registered),
            "present_names"   : sorted(present_names),
            "absent_names"    : sorted(absent_names)
        }

    def get_student_statistics(self):
        df           = self._get_clean_dataframe()
        all_students = self.stu_reg.get_all_students()
        total_school_days = df["Date"].nunique() if not df.empty else 0

        student_stats = []
        for student in all_students:
            days_present = (len(df[df["Name"] == student])
                            if not df.empty else 0)
            percentage   = self._safe_percentage(days_present,
                                                  total_school_days)
            student_stats.append({
                "name"        : student,
                "days_present": days_present,
                "total_days"  : total_school_days,
                "percentage"  : percentage,
                "status"      : self._get_attendance_status(percentage)
            })

        student_stats.sort(key=lambda x: x["percentage"], reverse=True)
        return student_stats

    def _get_attendance_status(self, percentage):
        if percentage >= 90:   return "Excellent"
        elif percentage >= 75: return "Good"
        elif percentage >= 60: return "Average"
        elif percentage >= 40: return "Poor"
        else:                  return "Critical"

    def get_daily_trend(self, days=14):
        df    = self._get_clean_dataframe()
        today = datetime.now()
        trend = []
        for i in range(days - 1, -1, -1):
            day     = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            count   = (len(df[df["Date"] == day_str])
                       if not df.empty else 0)
            trend.append({"date": day_str, "count": count})
        return trend

    def get_top_students(self, n=3):
        return self.get_student_statistics()[:n]

    def get_bottom_students(self, n=3):
        stats = self.get_student_statistics()
        return stats[-n:][::-1]

    def get_dashboard_data(self):
        df = self._get_clean_dataframe()
        return {
            "today"        : self.get_today_summary(),
            "students"     : self.get_student_statistics(),
            "trend"        : self.get_daily_trend(days=14),
            "top_students" : self.get_top_students(n=3),
            "low_students" : self.get_bottom_students(n=3),
            "total_records": len(df) if not df.empty else 0
        }


if __name__ == "__main__":
    manager = AttendanceManager()
    reg     = StudentRegistration()
    stats   = AttendanceStatistics(manager, reg)
    summary = stats.get_today_summary()
    print("Today's Summary:", summary)
