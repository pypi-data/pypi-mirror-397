"""Functions for uploading assignments to Gradescope."""

import io
import mimetypes
import pathlib

import requests
from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder

from gradescopeapi import DEFAULT_GRADESCOPE_BASE_URL
from dataclasses import dataclass
# from types import SimpleNamespace
# import json


@dataclass
class Owner:
    id: str
    active: bool
    initials: str
    name: str


@dataclass
class Submission:
    submission_id: str
    created_at: str
    owners: list[Owner]
    show_path: str
    active: bool
    activate_path: bool
    can_activate: bool
    score: str


class NoSubmission(Exception):
    pass


def upload_assignment(
    session: requests.Session,
    course_id: str,
    assignment_id: str,
    *files: io.TextIOWrapper,
    leaderboard_name: str | None = None,
    gradescope_base_url: str = DEFAULT_GRADESCOPE_BASE_URL,
) -> str | None:
    """Uploads given file objects to the specified assignment on Gradescope.

    Args:
        session (requests.Session): The session object to use for making HTTP requests.
        course_id (str): The ID of the course on Gradescope.
        assignment_id (str): The ID of the assignment on Gradescope.
        *files (io.TextIOWrapper): Variable number of file objects to upload.
        leaderboard_name (str | None, optional): The name of the leaderboard. Defaults to None.

    Returns:
        str | None: Link to submission if successful or None if unsuccessful.
    """
    GS_COURSE_ENDPOINT = f"{gradescope_base_url}/courses/{course_id}"
    GS_UPLOAD_ENDPOINT = f"{gradescope_base_url}/courses/{course_id}/assignments/{assignment_id}/submissions"

    # Get auth token
    # TODO: Refactor to helper function since it is needed in multiple places
    response = session.get(GS_COURSE_ENDPOINT)
    soup = BeautifulSoup(response.text, "html.parser")
    auth_token = soup.find("meta", {"name": "csrf-token"})["content"]

    # Format files for upload
    form_files = []
    for file in files:
        form_files.append(
            (
                "submission[files][]",
                (
                    pathlib.Path(file.name).name,  # get the filename from the path
                    file,
                    mimetypes.guess_type(file.name)[0],
                ),
            )
        )

    # Setup multipart form data
    fields = [
        ("utf8", "✓"),
        ("authenticity_token", auth_token),
        ("submission[method]", "upload"),
        *form_files,
    ]
    if leaderboard_name is not None:
        fields.append(("submission[leaderboard_name]", leaderboard_name))

    multipart = MultipartEncoder(fields=fields)

    headers = {
        "Content-Type": multipart.content_type,
        "Referer": GS_COURSE_ENDPOINT,
    }
    response = session.post(GS_UPLOAD_ENDPOINT, data=multipart, headers=headers)

    # Note: Response status code is always 200 even if upload was unsuccessful (e.g. past the due date,
    # missing form fields, etc.). The response from the server either redirects to the submission page (url)
    # if successful, or redirects to the Course homepage if unsuccessful.
    return (
        None
        if response.url == GS_COURSE_ENDPOINT or response.url.endswith("submissions")
        else response.url
    )


def get_submission_ids(
    session: requests.Session,
    course_id: str,
    assignment_id: str,
    submission_id: str,
    gradescope_base_url: str = DEFAULT_GRADESCOPE_BASE_URL,
) -> list[str]:
    """ """
    GS_PAST_SUBMISSIONS_ENDPOINT = f"{gradescope_base_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{submission_id}.json?content=react&only_keys[]=past_submissions"

    response = session.get(GS_PAST_SUBMISSIONS_ENDPOINT)
    response.raise_for_status()

    latest_submission = response.headers.get("Location", None)
    if latest_submission is None:
        raise NoSubmission(
            f"no submission found for assignment {assignment_id} in course {course_id}"
        )
    response.url

    return response.content


# def get_submission_ids(
#     session: requests.Session,
#     course_id: str,
#     assignment_id: str,
#     gradescope_base_url: str = DEFAULT_GRADESCOPE_BASE_URL,
# ) -> list[str]:
#     """ """
#     # Try getting most recent submission
#     GS_ASSIGNMENT_ENDPOINT = (
#         f"{gradescope_base_url}/courses/{course_id}/assignments/{assignment_id}"
#     )

#     headers = {
#         "Referer": GS_ASSIGNMENT_ENDPOINT,
#     }

#     response = session.get(
#         GS_ASSIGNMENT_ENDPOINT, headers=headers, allow_redirects=False
#     )
#     response.raise_for_status()
#     latest_submission = response.headers.get("Location", None)
#     if latest_submission is None:
#         raise NoSubmission(
#             f"no submission found for assignment {assignment_id} in course {course_id}"
#         )
#     response.url

#     return response.content
