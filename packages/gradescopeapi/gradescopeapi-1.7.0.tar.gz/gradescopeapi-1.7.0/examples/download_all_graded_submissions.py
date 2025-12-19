""" """

from gradescopeapi.classes.connection import GSConnection

# from gradescopeapi.classes.assignments import (
#     download_graded_assignment,
# )
import os
from dotenv import load_dotenv

load_dotenv()


GRADESCOPE_CI_STUDENT_EMAIL = os.getenv("GRADESCOPE_CI_STUDENT_EMAIL")
GRADESCOPE_CI_STUDENT_PASSWORD = os.getenv("GRADESCOPE_CI_STUDENT_PASSWORD")

# Create connection and login using env variables
connection = GSConnection()
connection.login(GRADESCOPE_CI_STUDENT_EMAIL, GRADESCOPE_CI_STUDENT_PASSWORD)

# Fetching all courses for user
courses = connection.account.get_courses()
for course_id in courses["student"]:
    print(courses["student"][course_id])

    # Getting all assignments for course
    assignments = connection.account.get_assignments(course_id)
    for assignment in assignments:
        print(assignment)

    # # Save bytes to disk
    # # Generate download file name if not set
    # if download_path is None:
    #     # expects a quoted filename, e.g. 'inline; filename="submission_372482786.pdf"'
    #     disposition = response.headers.get("Content-Disposition", f'filename="submission_{assignment_id}"')
    #     filename = disposition.split('filename="')[-1][:-1]
    #     download_path = f"./{filename}"

    # with open(download_path, "xb") as f:
    #     f.write(response.content)

# def get_submission_ids(
#     session: requests.Session,
#     course_id: str,
#     assignment_id: str,
#     gradescope_base_url: str = DEFAULT_GRADESCOPE_BASE_URL,
# ) -> list[str]:
#     return []
