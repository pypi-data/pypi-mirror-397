# from gradescopeapi.classes.assignments import download_graded_assignment

# import requests


# def test_valid_download_graded_assignment(create_session):
#     """Test valid download graded assignment for a student."""
#     # create test session
#     test_session = create_session("student")

#     course_id = "753413"
#     assignment_id = "7205866"
#     submission_id = "372482786"

#     bytes = download_graded_assignment(
#         test_session,
#         course_id,
#         assignment_id,
#         submission_id,
#     )
#     assert bytes


# def test_invalid_download_not_graded_assignment(create_session):
#     """Test invalid download not graded assignment for a student."""
#     # create test session
#     test_session = create_session("student")

#     course_id = "753413"
#     assignment_id = "4455030"
#     submission_id = "372486013"

#     try:
#         download_graded_assignment(
#             test_session,
#             course_id,
#             assignment_id,
#             submission_id,
#         )
#         assert False
#     except requests.exceptions.HTTPError as e:
#         assert e.response.status_code == 500  # HTTP 500 Internal Server Error

#     # # Save bytes to disk
#     # # Generate download file name if not set
#     # if download_path is None:
#     #     # expects a quoted filename, e.g. 'inline; filename="submission_372482786.pdf"'
#     #     disposition = response.headers.get("Content-Disposition", f'filename="submission_{assignment_id}"')
#     #     filename = disposition.split('filename="')[-1][:-1]
#     #     download_path = f"./{filename}"

#     # with open(download_path, "xb") as f:
#     #     f.write(response.content)
