from flask import Flask, render_template, request, redirect, session
from db import fetch_one, fetch_all, execute, hash_password, verify_password
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")


# ---------------------------
# HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register_choice():
    return render_template("register.html")


# -------------------------------------
# STUDENT REGISTRATION
# -------------------------------------
@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone", None)
        password = request.form["password"]

        # Check if email already exists
        existing_user = fetch_one(
            "SELECT * FROM users WHERE email=%s", (email,)
        )

        if existing_user:
            return "Error: Email already registered!"

        # Hash password
        hashed = hash_password(password)

        # Insert into database
        execute(
            "INSERT INTO users (role, name, email, phone, password_hash) VALUES (%s, %s, %s, %s, %s)",
            ("student", name, email, phone, hashed)
        )

        return redirect("/login/student")

    return render_template("register_student.html")

# -------------------------------------
# STUDENT LOGIN
# -------------------------------------
@app.route("/login/student", methods=["GET", "POST"])
def login_student():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Fetch user by email
        user = fetch_one(
            "SELECT * FROM users WHERE email=%s AND role='student'", 
            (email,)
        )

        if not user:
            return "Invalid email or not a student account."

        # Check hashed password
        if not verify_password(password, user["password_hash"]):
            return "Incorrect password."

        # Create session
        session["user_id"] = user["id"]
        session["role"] = "student"
        session["user_name"] = user["name"]

        return redirect("/student/dashboard")

    return render_template("login_student.html")

# -------------------------------------
# STUDENT DASHBOARD
# -------------------------------------
@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    return render_template("student_dashboard.html", name=session["user_name"])

# -------------------------------------
# STUDENT: VIEW ALL PROPERTIES
# -------------------------------------
@app.route("/student/properties")
def student_properties():
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    props = fetch_all("SELECT * FROM properties")

    return render_template("student_properties.html", props=props)

# -------------------------------------
# STUDENT: VIEW ROOMS IN PROPERTY
# -------------------------------------
@app.route("/student/property/<int:pid>/rooms")
def student_view_rooms(pid):
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    property_data = fetch_one("SELECT * FROM properties WHERE id=%s", (pid,))

    if not property_data:
        return "Property not found."

    rooms = fetch_all("""
        SELECT r.*, 
        (
            SELECT COUNT(*) 
            FROM bookings b 
            WHERE b.room_id = r.id AND b.status IN ('approved', 'checked_in')
        ) AS active_students
        FROM rooms r
        WHERE r.property_id = %s
    """, (pid,))

    return render_template("student_view_rooms.html", property=property_data, rooms=rooms)

# -------------------------------------
# STUDENT: BOOK A ROOM
# -------------------------------------
@app.route("/student/book/<int:room_id>", methods=["GET", "POST"])
def book_room(room_id):
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    # Fetch room
    room = fetch_one("SELECT * FROM rooms WHERE id=%s", (room_id,))
    if not room:
        return "Room not found."

    if request.method == "POST":
        check_in = request.form["check_in"]

        # Create booking with correct table column names
        execute(
            "INSERT INTO bookings (room_id, property_id, student_id, start_date, status) "
            "VALUES (%s, %s, %s, %s, 'pending')",
            (room_id, room["property_id"], session["user_id"], check_in)
        )

        return redirect("/student/bookings")

    return render_template("book_room.html", room=room)


# -------------------------------------
# STUDENT: VIEW BOOKINGS
# -------------------------------------
@app.route("/student/bookings")
def student_bookings():
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    bookings = fetch_all("""
        SELECT 
            b.id,
            b.start_date,
            b.end_date,
            b.status,
            r.room_no,
            p.name AS property_name,
            (
                SELECT status 
                FROM payments 
                WHERE booking_id = b.id
                ORDER BY id DESC
                LIMIT 1
            ) AS payment_status
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN properties p ON b.property_id = p.id
        WHERE b.student_id=%s
        ORDER BY b.id DESC
    """, (session["user_id"],))

    return render_template("student_bookings.html", bookings=bookings)






# -------------------------------------
# OWNER REGISTRATION
# -------------------------------------
@app.route("/register/owner", methods=["GET", "POST"])
def register_owner():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone", None)
        password = request.form["password"]

        # Check if email exists
        existing_user = fetch_one(
            "SELECT * FROM users WHERE email=%s", (email,)
        )

        if existing_user:
            return "Error: Email already registered!"

        hashed = hash_password(password)

        execute(
            "INSERT INTO users (role, name, email, phone, password_hash) VALUES (%s, %s, %s, %s, %s)",
            ("owner", name, email, phone, hashed)
        )

        return redirect("/login/owner")

    return render_template("register_owner.html")

# -------------------------------------
# OWNER LOGIN
# -------------------------------------
@app.route("/login/owner", methods=["GET", "POST"])
def login_owner():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = fetch_one(
            "SELECT * FROM users WHERE email=%s AND role='owner'", 
            (email,)
        )

        if not user:
            return "Invalid email or not an owner account."

        if not verify_password(password, user["password_hash"]):
            return "Incorrect password."

        session["user_id"] = user["id"]
        session["role"] = "owner"
        session["user_name"] = user["name"]

        return redirect("/owner/dashboard")

    return render_template("login_owner.html")


# -------------------------------------
# OWNER DASHBOARD
# -------------------------------------
@app.route("/owner/dashboard")
def owner_dashboard():
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    return render_template("owner_dashboard.html", name=session["user_name"])

# -------------------------------------
# ADD PROPERTY
# -------------------------------------
@app.route("/owner/property/add", methods=["GET", "POST"])
def add_property():
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    if request.method == "POST":

        name = request.form["name"]
        address = request.form["address"]
        city = request.form["city"]
        pincode = request.form.get("pincode")
        description = request.form.get("description")

        execute(
            "INSERT INTO properties (owner_id, name, address, city, pincode, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (session["user_id"], name, address, city, pincode, description)
        )

        return redirect("/owner/properties")

    return render_template("add_property.html")


# -------------------------------------
# VIEW PROPERTIES
# -------------------------------------
@app.route("/owner/properties")
def view_properties():
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    props = fetch_all(
        "SELECT * FROM properties WHERE owner_id=%s",
        (session["user_id"],)
    )

    return render_template("view_properties.html", props=props)

# -------------------------------------
# VIEW ROOMS OF A PROPERTY
# -------------------------------------
@app.route("/owner/property/<int:pid>/rooms")
def view_rooms(pid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    property_data = fetch_one(
        "SELECT * FROM properties WHERE id=%s AND owner_id=%s",
        (pid, session["user_id"])
    )

    if not property_data:
        return "Property not found or unauthorized."

    rooms = fetch_all(
        "SELECT * FROM rooms WHERE property_id=%s",
        (pid,)
    )

    return render_template("view_rooms.html", property=property_data, rooms=rooms)

# -------------------------------------
# ADD ROOM TO PROPERTY
# -------------------------------------
@app.route("/owner/property/<int:pid>/room/add", methods=["GET", "POST"])
def add_room(pid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    # Verify property belongs to owner
    property_data = fetch_one(
        "SELECT * FROM properties WHERE id=%s AND owner_id=%s",
        (pid, session["user_id"])
    )

    if not property_data:
        return "Unauthorized or invalid property"

    if request.method == "POST":

        room_no = request.form["room_no"]
        room_type = request.form["room_type"]
        bed_capacity = request.form["bed_capacity"]
        rent = request.form["rent"]
        deposit = request.form["deposit"]
        sharing = request.form["sharing"]

        execute(
            "INSERT INTO rooms (property_id, room_no, room_type, bed_capacity, rent, deposit, sharing) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (pid, room_no, room_type, bed_capacity, rent, deposit, sharing)
        )

        return redirect(f"/owner/property/{pid}/rooms")

    return render_template("add_room.html", property=property_data)

# -------------------------------------
# OWNER: VIEW ALL BOOKINGS FOR THEIR PROPERTIES
# -------------------------------------
@app.route("/owner/bookings")
def owner_bookings():
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    bookings = fetch_all("""
        SELECT b.id, b.start_date, b.status,
               r.room_no,
               p.name AS property_name,
               u.name AS student_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN properties p ON b.property_id = p.id
        JOIN users u ON b.student_id = u.id
        WHERE p.owner_id=%s
        ORDER BY b.id DESC
    """, (session["user_id"],))

    return render_template("owner_bookings.html", bookings=bookings)


@app.route("/owner/booking/<int:bid>/approve")
def approve_booking(bid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    # Attempt to approve
    success = execute(
        "UPDATE bookings SET status='approved' WHERE id=%s",
        (bid,)
    )

    if not success:
        return "Error: Could not approve booking (maybe room full)."

    return redirect("/owner/bookings")


@app.route("/owner/booking/<int:bid>/reject")
def reject_booking(bid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    execute(
        "UPDATE bookings SET status='rejected' WHERE id=%s",
        (bid,)
    )

    return redirect("/owner/bookings")

# -------------------------------------
# OWNER: CHECK-IN
# -------------------------------------
@app.route("/owner/booking/<int:bid>/checkin")
def checkin_booking(bid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    execute(
        "UPDATE bookings SET status='checked_in' WHERE id=%s",
        (bid,)
    )

    return redirect("/owner/bookings")


# -------------------------------------
# OWNER: CHECK-OUT
# -------------------------------------
@app.route("/owner/booking/<int:bid>/checkout")
def checkout_booking(bid):
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    execute(
        "UPDATE bookings SET status='checked_out', end_date=CURDATE() WHERE id=%s",
        (bid,)
    )

    return redirect("/owner/bookings")

# -------------------------------------
# STUDENT: PAY RENT
# -------------------------------------
@app.route("/student/pay/<int:bid>", methods=["GET", "POST"])
def pay_rent(bid):
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    # Fetch booking details
    booking = fetch_one("""
        SELECT b.*, r.room_no, p.name AS property_name, r.rent AS amount
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN properties p ON b.property_id = p.id
        WHERE b.id=%s AND b.student_id=%s
    """, (bid, session["user_id"]))

    if not booking:
        return "Booking not found or unauthorized."

    if request.method == "POST":
        method = request.form["method"]

        # Create payment record with PENDING status
        execute("""
            INSERT INTO payments (booking_id, amount, method, status)
            VALUES (%s, %s, %s, 'pending')
        """, (bid, booking["amount"], method))

        # Redirect to simulate payment success
        return redirect(f"/student/pay/confirm/{bid}")

    return render_template("payment.html", booking=booking)


# -------------------------------------
# STUDENT: CONFIRM PAYMENT (SIMULATION)
# -------------------------------------
@app.route("/student/pay/confirm/<int:bid>")
def confirm_payment(bid):
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    # Mark the latest payment as PAID
    execute("""
        UPDATE payments
        SET status='paid',
            txn_ref = CONCAT('TXN', UNIX_TIMESTAMP()),
            paid_at = NOW()
        WHERE booking_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (bid,))

    return redirect("/student/payments")


# -------------------------------------
# STUDENT: VIEW PAYMENT HISTORY
# -------------------------------------
@app.route("/student/payments")
def student_payments():
    if "user_id" not in session or session["role"] != "student":
        return redirect("/login/student")

    payments = fetch_all("""
        SELECT pay.*, r.room_no, p.name AS property_name
        FROM payments pay
        JOIN bookings b ON pay.booking_id = b.id
        JOIN rooms r ON b.room_id = r.id
        JOIN properties p ON b.property_id = p.id
        WHERE b.student_id=%s
        ORDER BY pay.id DESC
    """, (session["user_id"],))

    return render_template("student_payments.html", payments=payments)

# -------------------------------------
# OWNER: VIEW ALL PAYMENTS
# -------------------------------------
@app.route("/owner/payments")
def owner_payments():
    if "user_id" not in session or session["role"] != "owner":
        return redirect("/login/owner")

    owner_id = session["user_id"]

    payments = fetch_all("""
        SELECT 
            pay.*,
            u.name AS student_name,
            r.room_no,
            p.name AS property_name
        FROM payments pay
        JOIN bookings b ON pay.booking_id = b.id
        JOIN users u ON b.student_id = u.id
        JOIN rooms r ON b.room_id = r.id
        JOIN properties p ON b.property_id = p.id
        WHERE p.owner_id = %s
        ORDER BY pay.id DESC
    """, (owner_id,))

    return render_template("owner_payments.html", payments=payments)

# -------------------------------------
# LOGOUT FOR BOTH STUDENT & OWNER
# -------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")





# KEEP THIS ABSOLUTELY AT THE END
if __name__ == "__main__":
    app.run(debug=True)
