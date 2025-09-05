import csv
import json
import os
import shutil
from datetime import datetime

# =====================
# File paths
# =====================
STUDENTS_FILE = "students.csv"
COURSES_FILE = "courses.json"
ENROLLMENTS_FILE = "enrollments.csv"
LOG_FILE = "app.log"

# =====================
# Data structures
# =====================
students = {}   # dict[int, dict]
courses = {}    # dict[str, dict]
enrollments = []  # list[dict]

# =====================
# Helper functions
# =====================
def log_action(action: str):
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {action}\n")

# trying this out for more accurate output
def load_students():
    #students = {}
    if not os.path.exists("students.csv") or os.path.getsize("students.csv") == 0:
        # Create default students
        with open("students.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "full_name", "year", "gpa"])
            writer.writerow([1003, "Grace Hopper", 3, 4.0])
            writer.writerow([1004, "John von Neumann", 2, 3.8])
            writer.writerow([1005, "Marie Curie", 4, 3.6])

    # Now load it
    with open("students.csv", newline="") as f:
        redone = csv.DictReader(f)
        for row in redone:
          #  print("DEBUG student row:", row)   # <--- DEBUG PRINT
            try:
                sid = int(row["student_id"])
                students[sid] = {
                    "name": row["full_name"],
                    "year": int(row["year"]),
                    "gpa": float(row["gpa"])
                }
            except Exception as e:
                #print("DEBUG error:", e)       # <--- DEBUG PRINT
                continue
    #print("DEBUG loaded students:", students) # <--- DEBUG PRINT
    return students

# Save the students dictionary back into students.csv
def save_students():
    """Save the global 'students' dictionary into students.csv and make a backup."""
    backup_file = f"students_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    with open(STUDENTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "full_name", "year", "gpa"])  # header row
        for sid, data in students.items():
            writer.writerow([sid, data["name"], data["year"], data["gpa"]])
    shutil.copy(STUDENTS_FILE, backup_file)


# Just trying this out to see what it gives as output
def load_courses():
    if not os.path.exists("courses.json") or os.path.getsize("courses.json") == 0:
        default_courses = {
            "CS101": {"title": "Intro to Programming", "credits": 3, "capacity": 5, "prereqs": []},
            "CS201": {"title": "Data Structures", "credits": 4, "capacity": 4, "prereqs": ["CS101"]},
            "CS301": {"title": "Algorithms", "credits": 4, "capacity": 3, "prereqs": ["CS201"]},
            "CS401": {"title": "Operating Systems", "credits": 4, "capacity": 2, "prereqs": ["CS201"]},
            "CS501": {"title": "Machine Learning", "credits": 3, "capacity": 3, "prereqs": ["CS301"]}
        }
        with open("courses.json", "w") as f:
            json.dump(default_courses, f, indent=2)


def load_enrollments():
    global enrollments
    if not os.path.exists(ENROLLMENTS_FILE):
        return
    try:
        with open(ENROLLMENTS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    enrollments.append({
                        "student_id": int(row["student_id"]),
                        "course_code": row["course_code"],
                        "grade": float(row["grade"]) if row["grade"] else None
                    })
                except Exception:
                    continue
    except FileNotFoundError:
        pass

def save_courses():
    backup_file = f"courses_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    with open(COURSES_FILE, "w") as f:
        json.dump(courses, f, indent=2)
    shutil.copy(COURSES_FILE, backup_file)


def save_enrollments():
    backup_file = f"enrollments_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    with open(ENROLLMENTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "course_code", "grade"])
        for e in enrollments:
            writer.writerow([e["student_id"], e["course_code"], e["grade"] if e["grade"] is not None else ""])
    shutil.copy(ENROLLMENTS_FILE, backup_file)


def list_students():
    for sid, data in students.items():
        print(f"{sid}: {data['name']} (Year {data['year']}, GPA {data['gpa']})")


def list_courses():
    for code, info in courses.items():
        print(f"{code}: {info['title']} ({info['credits']} credits, capacity {info['capacity']})")


def add_student():
    try:
        sid = int(input("Enter student ID: ")) # sid == studentID
        if sid in students:
            print("Student already exists.")
            return
        name = input("Enter full name: ")
        year = int(input("Enter year (1-4): "))
        gpa = float(input("Enter GPA (0.0 - 4.0): "))
        students[sid] = {"name": name, "year": year, "gpa": gpa}
        log_action(f"Added student {sid} - {name}")
    except ValueError:
        print("Invalid input.")


def add_course():
    code = input("Enter course code: ")
    if code in courses:
        print("Course already exists.")
        return
    title = input("Enter course title: ")
    try:
        credits = int(input("Enter credits: "))
        capacity = int(input("Enter capacity: "))
        prereqs = input("Enter prereqs (comma separated): ").split(",") if input else []
        prereqs = [p.strip() for p in prereqs if p.strip()]
        courses[code] = {"title": title, "credits": credits, "capacity": capacity, "prereqs": prereqs}
        log_action(f"Added course {code} - {title}")
    except ValueError:
        print("Invalid input.")


def enroll_student():
    try:
        sid = int(input("Enter student ID: "))
        if sid not in students:
            print("Student not found.")
            return
        code = input("Enter course code: ")
        if code not in courses:
            print("Course not found.")
            return
        # check duplicate
        for e in enrollments:
            if e["student_id"] == sid and e["course_code"] == code:
                print("Already enrolled.")
                return
        # check capacity
        enrolled_count = sum(1 for e in enrollments if e["course_code"] == code)
        if enrolled_count >= courses[code]["capacity"]:
            print("Course is full.")
            return
        enrollments.append({"student_id": sid, "course_code": code, "grade": None})
        log_action(f"Enrolled student {sid} in {code}")
    except ValueError:
        print("Invalid input.")


def record_grade():
    try:
        sid = int(input("Enter student ID: "))
        code = input("Enter course code: ")
        for e in enrollments:
            if e["student_id"] == sid and e["course_code"] == code:
                grade = float(input("Enter grade (0-100): "))
                e["grade"] = grade
                log_action(f"Recorded grade {grade} for student {sid} in {code}")
                return
        print("Enrollment not found.")
    except ValueError:
        print("Invalid input.")


def show_transcript():
    try:
        sid = int(input("Enter student ID: "))
        if sid not in students:
            print("Student not found.")
            return
        print(f"Transcript for {students[sid]['name']}: ")
        total_points, total_credits = 0, 0
        for e in enrollments:
            if e["student_id"] == sid:
                code = e["course_code"]
                grade = e["grade"]
                print(f" - {code}: grade {grade}")
                if grade is not None:
                    total_points += grade
                    total_credits += 1
        gpa = total_points / total_credits if total_credits else 0
        print(f"Calculated GPA: {gpa:.2f}")
    except ValueError:
        print("Invalid input.")


def search():
    query = input("Enter name or course code: ").lower()
    for sid, data in students.items():
        if query in data["name"].lower():
            print(f"Found student: {sid} - {data['name']}")
    for code, info in courses.items():
        if query in code.lower():
            print(f"Found course: {code} - {info['title']}")


def analytics():
    print("1. Top N students by GPA")
    print("2. Course fill rates")
    print("3. Average grade per course")
    choice = input("Choose: ")
    if choice == "1":
        try:
            n = int(input("Enter N: "))
            sorted_students = sorted(students.items(), key=lambda x: x[1]["gpa"], reverse=True)
            for sid, data in sorted_students[:n]:
                print(f"{sid}: {data['name']} GPA {data['gpa']}")
        except ValueError:
            print("Invalid input.")
    elif choice == "2":
        for code, info in courses.items():
            enrolled_count = sum(1 for e in enrollments if e["course_code"] == code)
            fill_rate = (enrolled_count / info["capacity"]) * 100
            warn = " (Nearly full!)" if fill_rate > 90 else ""
            print(f"{code}: {fill_rate:.1f}% full{warn}")
    elif choice == "3":
        for code, info in courses.items():
            grades = [e["grade"] for e in enrollments if e["course_code"] == code and e["grade"] is not None]
            if grades:
                avg = sum(grades) / len(grades)
                print(f"{code}: average grade {avg:.2f}")


# =====================
# Main loop
# =====================
def main():
    load_students()
    load_courses()
    load_enrollments()

    while True:
        print("\n--- Campus Registrar ---")
        print("1. List students/courses")
        print("2. Add student")
        print("3. Add course")
        print("4. Enroll student in course")
        print("5. Record/update grade")
        print("6. Show a student transcript")
        print("7. Search")
        print("8. Save & backup data")
        print("9. Analytics")
        print("10. Exit")

        choice = input("Choose an option: ")
        

        if choice == "1":
            list_students()
            list_courses()
        elif choice == "2":
            add_student()
        elif choice == "3":
            add_course()
        elif choice == "4":
            enroll_student()
        elif choice == "5":
            record_grade()
        elif choice == "6":
            show_transcript()
        elif choice == "7":
            search()
        elif choice == "8":
            save_students()
            save_courses()
            save_enrollments()
            log_action("Data saved and backed up.")
            print("Data saved.")
        elif choice == "9":
            analytics()
        elif choice == "10":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
