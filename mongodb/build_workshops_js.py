import re
import ast
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR.parent / "relational" / "workshops_registrations.sql"
OUTPUT_JS = BASE_DIR / "workshops_load.js"


def main():
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    lines = sql.splitlines()

    insert_workshop = []
    insert_registrations = []
    workshops = []

    for line in lines:
        if line.strip().startswith("INSERT INTO Workshops"):
            insert_workshop.append(line)

    for line in lines:
        if line.strip().startswith("INSERT INTO Registrations"):
            insert_registrations.append(line)

    for line in insert_workshop:
        values = insert_values(line)
        if not values:
            continue
        workshops.append(values)

    regs_workshops = defaultdict(list)

    for line in insert_registrations:
        values = insert_values(line)
        if not values:
            continue

        workshop_id, student_id, reg_date = values

        regs_workshops[workshop_id].append(
            {
                "studentID": student_id,
                "registeredOn": reg_date
            }
        )

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        for workshop in workshops:
            workshop_id, title, category, event_date, location, capacity = workshop
            registrations = regs_workshops.get(workshop_id, [])

            regs_parts = []

            for registration in registrations:
                regs_parts.append(
                    "{studentID: "
                    + js_string(registration["studentID"])
                    + ", \nregisteredOn: "
                    + to_iso_date(registration["registeredOn"])
                    + " }\n"
                )

            regs_js = "[ " + ", ".join(regs_parts) + " ]"

            doc = (
                "{ _id: " + str(workshop_id)
                + ", title: " + js_string(title)
                + ", \ncategory: " + js_string(category)
                + ", \neventDate: " + to_iso_date(event_date)
                + ", \nlocation: " + js_string(location)
                + ", \ncapacity: " + str(capacity)
                + ", \nregistrations: " + regs_js
                + " }"
            )

            f.write(f"db.workshops.insertOne({doc});\n")

    print(f"MongoDB load file generated: {OUTPUT_JS}")


def insert_values(line):
    values = re.search(r"VALUES\s*\((.*)\);", line)

    if not values:
        return None

    values = values.group(1)
    values = re.sub(r"DATE\s*'([^']+)'", r"'\1'", values)

    return ast.literal_eval(f"({values})")


def js_string(value: str):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_iso_date(date_str: str):
    return f'ISODate("{date_str}T00:00:00Z")'


if __name__ == "__main__":
    main()