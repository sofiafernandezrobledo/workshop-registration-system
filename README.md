# Workshop Registration System

A workshop registration management system built with **Python, Tkinter, Oracle SQL and MongoDB**.

The project explores the same workshop registration domain using both a **relational database model** and a **document-oriented model**. It also includes a desktop application for interacting with the Oracle database and a Python script that transforms the relational dataset into MongoDB documents.

## Features

The desktop application allows users to:

- Connect to an Oracle database.
- Initialize the database from an SQL script.
- View workshops and registrations.
- Search workshops by ID, title or category.
- View students registered for a workshop.
- Check available seats.
- Register students for workshops.
- Prevent duplicate registrations.
- Prevent registrations when a workshop is full.
- Delete existing registrations.

The application uses parameterized SQL queries when interacting with the database.

## Technologies

- Python
- Tkinter
- Oracle Database
- `python-oracledb`
- SQL
- MongoDB
- JavaScript

## Project Structure

```text
workshop-registration-system/
│
├── app/
│   └── main.py
│
├── mongodb/
│   ├── build_workshops_js.py
│   ├── workshops_load.js
│   └── queries_commands.txt
│
├── relational/
│   └── workshops_registrations.sql
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Relational Database

The relational version of the project is stored in:

```text
relational/workshops_registrations.sql
```

The Oracle database contains two main tables:

```text
Workshops
    │
    │ 1
    │
    │ N
Registrations
```

A workshop contains information such as:

- Workshop ID
- Title
- Category
- Event date
- Location
- Capacity

Registrations associate students with workshops and store the corresponding registration date.

The SQL script creates the required database structure and inserts the sample data used by the application.

## Desktop Application

The desktop application is located in:

```text
app/main.py
```

It provides a graphical interface built with Tkinter for interacting with the Oracle database.

The main menu includes:

```text
1. View Table Contents
2. Search Workshops
3. Show Registered Students
4. Register a New Student
5. Delete a Registration
6. Exit
```

Before creating a new registration, the application checks that:

- The workshop exists.
- The workshop has available capacity.
- The student is not already registered.

## MongoDB Model

The project also contains a document-oriented representation of the same workshop dataset.

Instead of storing workshops and registrations in separate tables, each workshop is represented as a MongoDB document with its registrations embedded inside it.

Example:

```javascript
{
    _id: 101,
    title: "Intro to Data Visualization",
    category: "Tech",
    eventDate: ISODate("2025-11-05T00:00:00Z"),
    location: "Innovation Hall 204",
    capacity: 40,
    registrations: [
        {
            studentID: "G01230001",
            registeredOn: ISODate("2025-10-28T00:00:00Z")
        }
    ]
}
```

This makes it possible to compare relational and document-oriented approaches for the same application domain.

## SQL to MongoDB Transformation

The script:

```text
mongodb/build_workshops_js.py
```

reads the relational data from:

```text
relational/workshops_registrations.sql
```

and generates:

```text
mongodb/workshops_load.js
```

The generated JavaScript file contains MongoDB `insertOne()` commands.

Registrations belonging to the same workshop are grouped and embedded inside the corresponding workshop document.

## MongoDB Queries

Example MongoDB queries and aggregation pipelines are included in:

```text
mongodb/queries_commands.txt
```

They include operations such as:

- Counting workshop documents.
- Counting total registrations.
- Filtering workshops by category and capacity.
- Filtering workshops by event date.
- Finding workshops with multiple registrations.
- Finding students registered for multiple workshops.

## Relational vs Document Model

| Relational Model | Document Model |
|---|---|
| Oracle Database | MongoDB |
| SQL | MongoDB Query Language |
| `Workshops` and `Registrations` tables | Workshop documents |
| Registrations stored separately | Registrations embedded inside workshops |
| Foreign-key relationships | Nested document structure |
| SQL queries | Find queries and aggregation pipelines |

## Requirements

Python 3 is required.

Install the Python dependency from the project root:

```bash
pip install -r requirements.txt
```

The project uses:

```text
oracledb
```

An Oracle Database connection is required to run the desktop application.

MongoDB is required only for the document-oriented part of the project.

## Running the Oracle Application

From the project root, run:

```bash
python app/main.py
```

The application asks for:

1. Oracle username.
2. Oracle password.
3. The path to the SQL initialization script.

Use:

```text
relational/workshops_registrations.sql
```

as the initialization script.

After the database has been initialized successfully, the main application interface will be displayed.

## Generating the MongoDB Dataset

From the project root, run:

```bash
python mongodb/build_workshops_js.py
```

The script transforms the relational dataset into MongoDB documents and generates:

```text
mongodb/workshops_load.js
```

This file can then be executed in MongoDB to populate the `workshops` collection.

## Purpose

The project demonstrates how the same data can be represented and queried using two different database paradigms.

It combines:

- Relational database design.
- SQL queries and data manipulation.
- Oracle database connectivity from Python.
- Desktop GUI development.
- MongoDB document modeling.
- MongoDB aggregation queries.
- Automated transformation from relational data to document-oriented data.
