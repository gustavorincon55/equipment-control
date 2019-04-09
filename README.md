# equipment-control

Administrative tool to keep track of claims among other things.

Administrative tool meant to be used by a team, to keep track of equipment claims. This tool was created by me to solve the need of a stable and fast tool to keep track of multiple claims with multiple attachments. 

Features:

- Add claim.
- Quick edit and full edit mode.
- Separates claims by country.
- Add attachment to claim.
- Download attachment.
- Erase attachment.
- Log in and registration.
- Backup (will create a .csv with all the text data and will download all the attachments organized by units and date).

Thecnologies:

- Flask (backend framework).
- Flask templates (jinja).
- Python.
- SQL.
- SQLAlchemy.
- JavaScript.
- Ajax.
- Bootstrap.
- HTML/CSS.

Motivation:
At my job, me and my coworkers had to rely on multiple excel spreadsheets to keep track of claims (with attachments). Keep in mind that excel doesn’t have a native solution to handle comfortably multiple attachments like a database. We had to rely on multiple objects to have attachments on the spreadsheet, which in turn created a highly unstable spreadsheet that crashed constantly and took a long time to open and save. This is mostly due to it having to load all of the objects on the spreadsheet every time it opened. Also, to add and remove objects in a clear and organized way is relatively time consuming and error prone when you handle multiple claims and multiple attachments. 



