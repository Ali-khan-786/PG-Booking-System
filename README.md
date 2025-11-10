# PG / Hostel Booking System  
A full-stack **Flask + MySQL** project designed as part of a **Database Management Systems (DBMS)** course.  
The system demonstrates real–world use of relational databases, CRUD operations, triggers, foreign key constraints, and multi–role authentication.

This project allows **students** to find and book PG/hostel rooms, and **property owners** to list and manage their properties.  
It showcases all important aspects of a DBMS project — including schema design, data validation, room availability logic, and payment tracking.

---

## ✅ Features

### 🔐 User Authentication
- Student registration & login  
- Owner registration & login  
- Secure password hashing  
- Session-based login system  

---

## 🏠 Student Features
- Browse available PG properties  
- View rooms (single / double / triple / dorm)  
- Book a room (start date, optional end date)  
- View booking history  
- Check booking status (pending, approved, rejected, etc.)  
- Make payments (mock payment system)  
- Prevent paying twice for same booking  

---

## 🏢 Owner Features
- Add properties (name, address, city, description, etc.)  
- Add rooms inside a property  
- Manage booking requests  
- Approve / Reject bookings  
- View student payment status  
- Payment history dashboard  

---

## 🛢️ Database Design (MySQL)

### Tables Used:
1. **users**  
2. **properties**  
3. **rooms**  
4. **bookings**  
5. **payments**

Triggers:
- **trg_capacity_guard** — prevents overbooking based on bed capacity

The complete clean SQL schema is available in: 
sql/pg_booking.sql


---

## ⚙️ Tech Stack

### Backend:
- Python  
- Flask  
- MySQL  
- mysql-connector-python  

### Frontend:
- HTML (Jinja templates)  
- Bootstrap 5  

### Tools:
- MySQL Workbench  
- VS Code  

---

## 🚀 How to Run the Project Locally

### 1. Clone the repository
git clone <link for the files](https://github.com/Ali-khan-786/PG-Booking-System)>
cd PG-Booking-System

### 2. Create a Virtual Environment
python -m venv venv
 Activate it:
 On Windows:venv\Scripts\activate
 On macOS/Linux:source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Create a `.env` File
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=pg_booking
FLASK_SECRET=your_secret_key

### 5. Import the SQL Schema
Open MySQL Workbench
Go to File → Open SQL Script
Select:sql/pg_booking.sql
Run the script to create all tables + triggers.

### 6. Start the Flask Server
Run:python app.py
Now open your browser:http://127.0.0.1:5000

---

📁 Project Structure
PG-Booking-System/
│
├── app.py
├── db.py
├── requirements.txt
├── .env.example
│
├── templates/
│   ├── index.html
│   ├── login_student.html
│   ├── login_owner.html
│   ├── register.html
│   ├── register_student.html
│   ├── register_owner.html
│   ├── student_dashboard.html
│   ├── owner_dashboard.html
│   └── other pages...
│
├── sql/
│   └── pg_booking.sql
│
└── README.md


## ✅ Why This Project is Good for DBMS Submission

- Proper use of **ER modeling**  
- Strong foreign key relationships  
- Real business logic (room capacity, payment rules)  
- Secure authentication & sessions  
- Database triggers for automatic validation  
- Clean SQL export  
- Frontend + Backend integration  

Your teacher will understand that you built a complete end-to-end DBMS system.

---

## 📌 Future Improvements (Optional)
- Admin dashboard  
- Complaint management system  
- Monthly rent cycle  
- Email notifications  
- Automatic vacancy calculation  

---

## ✅ Author  
**Ali Khan**  
B.Tech Student  

---


