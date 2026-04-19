#!/usr/bin/env python3

import sys
import argparse
import getpass
import mysql.connector
from mysql.connector import Error


# db connection
 
def get_connection(host, user, password):
    """Return a MySQL connection using provided credentials."""
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database="academic_insti"
    )


FAIL_GRADES = ('U', 'E')
SEM  = 'Even'
YEAR = 2006


# helpers

def print_header(title: str):
    print("\n" + "═" * 55)
    print(f"  {title}")
    print("═" * 55)
 
 
def print_success(msg: str):
    print(f"\n  ✔  {msg}")
 
 
def print_error(msg: str):
    print(f"\n  ✘  {msg}")
 
 
def print_info(msg: str):
    print(f"     {msg}")



# add course to even sem with details

def add_course(conn):
    print_header("FEATURE 1 — Add Course  (Even Semester 2006)")
 
    dept_id    = input("\n  Enter Department ID   : ").strip()
    course_id  = input("  Enter Course ID       : ").strip()
    teacher_id = input("  Enter Teacher (Emp) ID: ").strip()
    classroom  = input("  Enter Classroom       : ").strip()
 
    cursor = conn.cursor(dictionary=True)


    # validating dept exists
    cursor.execute("SELECT deptId, name FROM department WHERE deptId = %s", (dept_id,))
    dept = cursor.fetchone()
    if not dept:
        print_error(f"Department '{dept_id}' does not exist.")
        cursor.close()
        return
    print_info(f"Department found: {dept['name']}")



    # validating course exists and belongs to this dept
    cursor.execute(
        "SELECT courseId, cname, deptNo FROM course WHERE courseId = %s",
        (course_id,)
    )
    course = cursor.fetchone()
    if not course:
        print_error(f"Course '{course_id}' does not exist in the database.")
        cursor.close()
        return
    if course['deptNo'] != dept_id:
        print_error(
            f"Course '{course_id}' ({course['cname']}) belongs to "
            f"dept '{course['deptNo']}', not dept '{dept_id}'."
        )
        cursor.close()
        return
    print_info(f"Course found: {course['cname']}")



    # validating teacher exists and belongs to this dept
    cursor.execute(
        "SELECT empId, name, deptNo FROM professor WHERE empId = %s",
        (teacher_id,)
    )
    teacher = cursor.fetchone()
    if not teacher:
        print_error(f"Professor with empId '{teacher_id}' does not exist.")
        cursor.close()
        return
    if teacher['deptNo'] != dept_id:
        print_error(
            f"Professor '{teacher_id}' ({teacher['name']}) belongs to "
            f"dept '{teacher['deptNo']}', not dept '{dept_id}'."
        )
        cursor.close()
        return
    print_info(f"Professor found: {teacher['name']}")


    # checkign for duplicate teaching entry in the same year/sem
    cursor.execute(
        """SELECT 1 FROM teaching
           WHERE empId=%s AND courseId=%s AND sem=%s AND year=%s""",
        (teacher_id, course_id, SEM, YEAR)
    )
    if cursor.fetchone():
        print_error(
            f"Professor '{teacher_id}' is already assigned to course "
            f"'{course_id}' in Even 2006."
        )
        cursor.close()
        return
 


    # insert data into teaching
    cursor.execute(
        """INSERT INTO teaching (empId, courseId, sem, year, classRoom)
           VALUES (%s, %s, %s, %s, %s)""",
        (teacher_id, course_id, SEM, YEAR, classroom)
    )
    conn.commit()
 
    print_success(
        f"Course '{course_id}' ({course['cname']}) successfully added!\n"
        f"     Taught by : {teacher['name']}  |  Room: {classroom}  |  {SEM} {YEAR}"
    )
    cursor.close()



# enroll student

def enroll_student(conn):


    print_header("FEATURE 2 — Student Enrollment  (Even Semester 2006)")
 
    roll_no = input("\n  Enter Student Roll No : ").strip()
    cursor = conn.cursor(dictionary=True)
 
    # 1. Validate student exists
    cursor.execute(
        "SELECT rollNo, name, deptNo FROM student WHERE rollNo = %s",
        (roll_no,)
    )
    student = cursor.fetchone()
    if not student:
        print_error(f"Student with roll no '{roll_no}' does not exist.")
        cursor.close()
        return
    print_info(f"Student found: {student['name']}  (Dept: {student['deptNo']})")
 
    # 2. Get course IDs to enroll in
    raw = input("  Enter Course ID(s) (comma-separated): ").strip()
    course_ids = [c.strip() for c in raw.split(",") if c.strip()]
    if not course_ids:
        print_error("No course IDs provided.")
        cursor.close()
        return
 
    print()
    enrolled_any = False
 
    for course_id in course_ids:
        print(f"  ── Processing course: {course_id}")
 
        # 3. Check course exists
        cursor.execute(
            "SELECT courseId, cname FROM course WHERE courseId = %s",
            (course_id,)
        )
        course = cursor.fetchone()
        if not course:
            print_error(f"Course '{course_id}' not found. Skipping.")
            print()
            continue
 
        # 4 Check if professor is teaching this course in Even 2006
        cursor.execute(
            """SELECT empId, classRoom FROM teaching
               WHERE courseId=%s AND sem=%s AND year=%s""",
            (course_id, SEM, YEAR)
        )
        teaching_record = cursor.fetchone()
        if not teaching_record:
            print_error(
                f"Course '{course_id}' ({course['cname']}) is not being taught in Even 2006. "
                f"Cannot enroll. Skipping."
            )
            print()
            continue
        
        # Get professor info for display
        prof_id = teaching_record['empId']
        cursor.execute(
            "SELECT name FROM professor WHERE empId = %s",
            (prof_id,)
        )
        prof_info = cursor.fetchone()
        prof_name = prof_info['name'] if prof_info else "Unknown"
 
        # 5. Check if already enrolled
        cursor.execute(
            """SELECT 1 FROM enrollment
               WHERE rollNo=%s AND courseId=%s AND sem=%s AND year=%s""",
            (roll_no, course_id, SEM, YEAR)
        )
        if cursor.fetchone():
            print_error(f"Already enrolled in '{course_id}' ({course['cname']}) for Even 2006.")
            print()
            continue
 
        # 6 Check if student has taken this course in previous semesters (before 2006)
        cursor.execute(
            """SELECT grade FROM enrollment
               WHERE rollNo=%s AND courseId=%s AND year < %s""",
            (roll_no, course_id, YEAR)
        )
        previous_attempts = cursor.fetchall()
        
        if previous_attempts:
            # Student has attempted this course before - check if they passed
            has_passed = any(r['grade'] not in FAIL_GRADES for r in previous_attempts)
            
            if has_passed:
                # Student passed the course, no need to retake (regardless of any failures)
                print_error(
                    f"Student already passed '{course_id}' ({course['cname']}) in a previous semester. "
                    f"Cannot re-enroll. Skipping."
                )
                print()
                continue
            # If only failed in previous attempts, allow retake (fall through to next checks)
 
        #  Fetch prerequisites for this course
        cursor.execute(
            "SELECT preReqCourse FROM prerequisite WHERE courseId = %s",
            (course_id,)
        )
        prereqs = [row['preReqCourse'] for row in cursor.fetchall()]
 
        # 6. Check each prerequisite
        failed_prereqs  = []
        missing_prereqs = []
 
        for prereq_id in prereqs:
            cursor.execute(
                """SELECT grade FROM enrollment
                   WHERE rollNo = %s AND courseId = %s""",
                (roll_no, prereq_id)
            )
            records = cursor.fetchall()
 
            if not records:
                missing_prereqs.append(prereq_id)
            else:
                # Student attempted this prereq — check if they passed in any attempt
                passed = any(r['grade'] not in FAIL_GRADES for r in records)
                if not passed:
                    failed_prereqs.append(prereq_id)
 
        
        if missing_prereqs or failed_prereqs:
            print_error(f"Cannot enroll in '{course_id}' ({course['cname']}):")
            if missing_prereqs:
                print_info(f"  Not enrolled  : {', '.join(missing_prereqs)}")
            if failed_prereqs:
                print_info(f"  Failed/incomplete: {', '.join(failed_prereqs)}")
            print()
            continue
 
        # enrolling
        cursor.execute(
            """INSERT INTO enrollment (rollNo, courseId, sem, year, grade)
               VALUES (%s, %s, %s, %s, NULL)""",
            (roll_no, course_id, SEM, YEAR)
        )
        conn.commit()
 
        prereq_msg = (
            f"  Prerequisites cleared: {', '.join(prereqs)}"
            if prereqs else "  No prerequisites required."
        )
        print_success(
            f"Enrolled in '{course_id}' ({course['cname']}) — Even 2006"
        )
        print_info(f"  Taught by: {prof_name}  |  Room: {teaching_record['classRoom']}")
        print_info(prereq_msg)
        print()
        enrolled_any = True
 
    if enrolled_any:
        print_info("Enrollment process complete.")
    else:
        print_info("No new enrollments were made.")
 
    cursor.close()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Academic Institution DB — Assignment 4A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python main.py -u root -p mypassword\n"
               "  python main.py --user root --password mypassword\n"
               "  python main.py -u root          # prompts for password\n"
               "  python main.py --host 192.168.1.5 -u admin -p secret\n"
    )
    parser.add_argument("-u", "--user",     default="root",      help="MySQL username (default: root)")
    parser.add_argument("-p", "--password", default=None,        help="MySQL password (omit to be prompted)")
    parser.add_argument(      "--host",     default="localhost", help="MySQL host (default: localhost)")
    return parser.parse_args()
 


def main():

    args = parse_args()
 
    # If password not provided as arg, prompt securely (no echo)
    if args.password is None:
        args.password = getpass.getpass(f"  MySQL password for '{args.user}': ")
    print("\n" + "═" * 55)
    print("   Academic Institution DB — Assignment 4A")
    print("═" * 55)


    try:
        conn = get_connection(args.host, args.user, args.password)
        print_info(f"Connected as '{args.user}' to database 'academic_insti'.")
    except Error as e:
        print_error(f"Could not connect to database: {e}")
        sys.exit(1)


    while True:

        print("\n  MAIN MENU")
        print("  ─────────────────────────────────────")
        print("  1. Add course (Even Semester 2006)")
        print("  2. Enroll student (Even Semester 2006)")
        print("  3. Exit")
        print("  ─────────────────────────────────────")
        choice = input("  Enter choice [1/2/3]: ").strip()

        if choice == "1":
            try:
                add_course(conn)
            except Error as e:
                print_error(f"Database error: {e}")

        elif choice == "2":
            try:
                enroll_student(conn)
            except Error as e:
                print_error(f"Database error: {e}")


        elif choice == "3":
            print("\n  Closing!\n")
            break
 
        else:
            print_error("Invalid choice. Enter 1, 2, or 3.")
    
    conn.close()


if __name__ == "__main__":
    main()