#  Qatar Foundation Admin Portal

A full-stack web application built using Flask that allows administrators to manage internship and opportunity listings efficiently. This project was developed as part of an internship assessment.

---

##  Features

*  Admin Signup & Login (Authentication)
*  Forgot Password with secure reset token (1-hour expiry)
*  Admin Dashboard
*  Add new opportunities
*  Edit existing opportunities
*  Delete opportunities with confirmation
*  View detailed opportunity information
*  Each admin can only access their own data
*  Data stored in database 

---

##  Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite

---

##  Project Structure

****bash

├── qatar_portal/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── __init__.py
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   ├── templates/
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── forgot_password.html
│   │   └── reset_password.html
│   │
│   ├── run.py
│   └── requirements.txt
│
└── README.md
****

---

##  How to Run Locally

*** bash
# Step 1: Navigate to project folder
cd qatar_portal

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the application
python run.py

***

##  Access the Application

Open your browser and go to:

***
http://localhost:5000
***
##  Author

**Md Abdul Basid**
Computer Science And Engineering (Data Science)

---
