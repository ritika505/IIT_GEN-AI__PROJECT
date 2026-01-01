import json

# input & output files
json_file = "sunbeam_modular_courses_full.json"
txt_file = "sunbeam_modular_courses_full.txt"

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(txt_file, "w", encoding="utf-8") as f:
    for idx, course in enumerate(data, start=1):
        f.write(f"================ COURSE {idx} ================\n")
        f.write(f"URL            : {course.get('url')}\n")
        f.write(f"Course Name    : {course.get('Course Name')}\n")
        f.write(f"Duration       : {course.get('Duration')}\n")
        f.write(f"Batch Schedule : {course.get('Batch Schedule')}\n")
        f.write(f"Schedule       : {course.get('Schedule')}\n")
        f.write(f"Timings        : {course.get('Timings')}\n")
        f.write(f"Fees           : {course.get('Fees')}\n\n")

        # Syllabus
        f.write("---- SYLLABUS ----\n")
        syllabus = course.get("Sections", {}).get("Syllabus", [])
        if syllabus:
            for i, item in enumerate(syllabus, start=1):
                f.write(f"{i}. {item}\n")
        else:
            f.write("Not Available\n")

        # Prerequisites
        f.write("\n---- PREREQUISITES ----\n")
        prereq = course.get("Sections", {}).get("Prerequisites", [])
        if prereq:
            for i, item in enumerate(prereq, start=1):
                f.write(f"{i}. {item}\n")
        else:
            f.write("Not Available\n")

        f.write("\n\n")

print("✅ JSON successfully converted to TXT")
