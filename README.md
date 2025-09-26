# Payroll-Automator
## Project Overview
This repository contains a Flask-based payroll automation system that calculates employee payroll in compliance with the 2025 Kenyan tax laws. It automates salary computations, statutory deductions (PAYE, SHIF, NSSF, AHL), and generates professional PDF payslips and a P10 csv.

The project is designed to eliminate manual errors, save processing time, and ensure regulatory compliance for SMEs, accounting firms, and HR departments.
### Goal
The goal was to:

Build a lightweight payroll system using Python and Flask that automates payroll calculations, generates payslips in PDF, and exports statutory reports (P10).

## Features
1. Secure User Authentication: Employs Flask-Login for robust user registration, login, and session management, ensuring that all user data is protected. Passwords are securely hashed using Werkzeug.

2. Automated Payroll Calculations: Automatically calculates all Kenyan statutory deductions, including PAYE (with tax relief), NSSF (Tier I & II), SHIF, and the Affordable Housing Levy (AHL), compliant with the latest regulations.

3. Dynamic PDF Payslip Generation: Generates professional, detailed PDF payslips for any employee and any payroll period on the fly using the ReportLab library.

4. KRA P10 Tax Report Export: Creates and downloads a CSV file formatted as a KRA P10 tax return, consolidating all employee payroll data for a specific period for easy submission.

5. Role-Based Access Control: Differentiates between regular users and administrators. Admins have the authority to manage and clear all records in the system, while regular users are restricted to managing only their own employees.
## How it Works
1. Backend Framework: The core of the application is built with Flask, a lightweight and powerful Python web framework. It handles all routing, request handling, and interaction with the database.

2. Database Management: SQLAlchemy is used as the Object-Relational Mapper (ORM), which allows the application to interact with a SQLite database using simple Python objects. The models.py file defines the schema for the User, Employee, and Payroll tables and the relationships between them.

3. Authentication: When a user registers, their password is automatically hashed and stored in the database. During login, Flask-Login securely verifies their credentials and creates a user session, giving them access to the dashboard.

4. Payroll Calculation: When an employee is added or their payroll is processed, the application gathers their salary information and passes it to the payroll_calculator.py module. This module contains dedicated functions for each statutory deduction (PAYE, NSSF, etc.), calculates the final net pay, and returns a complete, structured breakdown.

5. Data Persistence: The results from the payroll calculation are used to create a new Payroll record, which is then saved to the database and linked to the corresponding Employee.

6. Dynamic File Generation:

 - PDF Payslips: When a user requests a payslip, the generate_pdf.py module uses ReportLab to draw the document in memory. It pulls the relevant employee and payroll data from the database, formats it into styled tables and paragraphs, and creates a PDF file. This file is then sent directly to the user's browser as a download, without ever being saved on the server.

- CSV Reports: Similarly, when a KRA P10 report is requested, the application fetches all relevant payroll records, formats them into a CSV structure in memory using Python's csv module, and delivers it to the user as a downloadable file.

## Requirements
The requirements can be found in the requirements.txt

## Usage
1. Run locally
 - Clone this repository:  
   ```git clone https://github.com/cabralchege/Payroll-Automator```  
   ```cd Payroll_Automator```  

 - Create and activate a virtual environment:  
  ```python -m venv venv```  
  ```source venv/bin/activate``` # For Linux/ Mac users  
  ```venv\Scripts\activate```    # For windows users  

  - Install dependencies:  
  ```pip install -r requirements.txt```  

  - Start the Flask app:  
  ```python app.py```  

  - Open your browser at [Local host](http://127.0.0.1:5000)  
## Project Structure
/Payroll-Automator
│── app.py              # Flask web app entry point
│── generate_pdf.py     # Handles payslip generation with ReportLab
│── requirements.txt    # Project dependencies
│── README.md           # Documentation
│── /templates          # HTML templates for Flask
│── /static             # CSS and JS files
│── models.py           # Database models

## Technical Details
- Framework: Flask (2.3.3), a lightweight and powerful WSGI web application framework in Python. It provides the core routing, request handling, and application context.


- Database: SQLite is used as the database engine for simplicity and portability. The application is configured to use a file-based database named payroll.db.

- Object-Relational Mapper (ORM): Flask-SQLAlchemy (3.0.5) is used to manage the database schema and interactions in an object-oriented way. It simplifies database operations by mapping Python classes to database tables.

- Authentication: Secure user authentication and session management are handled by Flask-Login. Passwords are not stored in plain text; instead, they are securely hashed and verified using Werkzeug's (2.3.7) security utilities.

- PDF Generation: PDF payslips are generated dynamically in memory using the ReportLab (4.0.4) library. This is a powerful toolkit for creating rich PDF documents programmatically.

## Results
- Simplifies payroll calculations for small businesses and and accountants.
- Produces professional looking payslips in pdf fomat.
- Generates an uploadable P10 csv that can be used for filing PAYE monthly.

## Blog
You can read more on this blog (here)[https://thecabralperspective.hashnode.dev/how-i-built-an-automated-payroll-system-in-python-and-flask]
## Contact
For questions or collaboration, contact cabralowiro@gmail.com or open an issue on the repo

## References
1. Python Documentation
2. Flask Documentation
3. ReportLab Documentation
4. KRA Website

## Licence
- MIT License Copyright (c) 2025 (Chege Cabral)
- - [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

