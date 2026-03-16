import csv
import json
import os
import requests

MOODLE_URL = os.environ["MOODLE_URL"]
MOODLE_TOKEN = os.environ["MOODLE_TOKEN"]

COURSE_ID = 11
ACTIVITY_ID = 166

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAP_FILE = os.path.join(BASE_DIR, "github_moodle_map.csv")
RESULTS_FILE = os.path.join(BASE_DIR, "results.json")


def get_grade_from_results():
    with open("results.json", "r") as f:
        data = json.load(f)
        return data["score"]


def load_mapping(csv_file):
    mapping = {}

    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            github_username = row["github_username"].strip()
            moodle_user_id = row["moodle_user_id"].strip()

            if github_username and moodle_user_id:
                mapping[github_username] = int(moodle_user_id)

    return mapping


def send_grade_to_moodle(moodle_user_id, grade):

    payload = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_grades_update_grades",
        "moodlewsrestformat": "json",
        "source": "GitHub Classroom",
        "courseid": COURSE_ID,
        "component": "mod_lti",
        "activityid": ACTIVITY_ID,
        "itemnumber": 0,
        "grades[0][studentid]": moodle_user_id,
        "grades[0][grade]": grade,
    }

    response = requests.post(MOODLE_URL, data=payload, timeout=30)
    response.raise_for_status()

    return response.json()


def main():

    github_username = os.environ["GITHUB_USERNAME"]
    grade = float(get_grade_from_results())

    mapping = load_mapping(MAP_FILE)

    if github_username not in mapping:
        print(f"Skipping: GitHub username '{github_username}' not found in mapping file.")
        return

    moodle_user_id = mapping[github_username]

    print(f"Found Moodle user ID {moodle_user_id} for GitHub user '{github_username}'")
    print(f"Grade from results.json: {grade}")

    result = send_grade_to_moodle(moodle_user_id, grade)

    print("Moodle response:")
    print(result)


if __name__ == "__main__":
    main()
