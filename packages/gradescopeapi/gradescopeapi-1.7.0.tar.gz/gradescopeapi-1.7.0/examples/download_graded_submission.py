from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.assignments import download_graded_assignment

# create connection and login
connection = GSConnection()
connection.login("email@domain.com", "password")

# replace values below
course_id = "123456"
assignment_id = "1234567"
submission_id = "123456789"

# download graded submission (can take a while)
bytes = download_graded_assignment(
    connection.session,
    course_id,
    assignment_id,
    submission_id,
)

# save bytes to disk
with open(f"{submission_id}.pdf", "xb") as f:
    f.write(bytes)
