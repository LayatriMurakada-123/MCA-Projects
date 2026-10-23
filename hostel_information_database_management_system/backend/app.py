from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "hostel.db"

app = Flask(__name__, template_folder="templates", static_folder="static")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    with open(BASE_DIR.parent / "database" / "schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/students")
def students_page():
    return render_template("students.html")

@app.route("/rooms")
def rooms_page():
    return render_template("rooms.html")

@app.route("/staff")
def staff_page():
    return render_template("staff.html")

@app.route("/fees")
def fees_page():
    return render_template("fees.html")

@app.route("/complaints")
def complaints_page():
    return render_template("complaints.html")

@app.get("/api/dashboard")
def dashboard():
    conn = get_db()
    data = {
        "students": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "rooms": conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
        "available_rooms": conn.execute("SELECT COUNT(*) FROM rooms WHERE occupied < capacity").fetchone()[0],
        "pending_complaints": conn.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'").fetchone()[0],
        "total_fees": conn.execute("SELECT COALESCE(SUM(amount),0) FROM fees").fetchone()[0],
        "paid_fees": conn.execute("SELECT COALESCE(SUM(amount),0) FROM fees WHERE status='Paid'").fetchone()[0]
    }
    conn.close()
    return jsonify(data)

@app.get("/api/students")
def get_students():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.*, r.room_number
        FROM students s LEFT JOIN rooms r ON s.room_id = r.id
        ORDER BY s.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/students")
def add_student():
    data = request.get_json()
    required = ["name", "email", "phone", "course", "year"]
    if not all(str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "All required fields must be filled."}), 400

    conn = get_db()
    try:
        room_id = data.get("room_id") or None
        if room_id:
            room = conn.execute("SELECT occupied, capacity FROM rooms WHERE id=?", (room_id,)).fetchone()
            if not room:
                return jsonify({"error": "Room not found."}), 404
            if room["occupied"] >= room["capacity"]:
                return jsonify({"error": "Selected room is full."}), 400

        conn.execute("""
            INSERT INTO students(name,email,phone,course,year,room_id)
            VALUES(?,?,?,?,?,?)
        """, (data["name"], data["email"], data["phone"], data["course"], data["year"], room_id))
        if room_id:
            conn.execute("UPDATE rooms SET occupied=occupied+1 WHERE id=?", (room_id,))
        conn.commit()
        return jsonify({"message": "Student added successfully."}), 201
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.put("/api/students/<int:student_id>")
def update_student(student_id):
    data = request.get_json()
    conn = get_db()
    old = conn.execute("SELECT room_id FROM students WHERE id=?", (student_id,)).fetchone()
    if not old:
        conn.close()
        return jsonify({"error": "Student not found."}), 404

    new_room = data.get("room_id") or None
    try:
        if new_room:
            room = conn.execute("SELECT occupied, capacity FROM rooms WHERE id=?", (new_room,)).fetchone()
            if not room:
                return jsonify({"error": "Room not found."}), 404
            if room["occupied"] >= room["capacity"] and new_room != old["room_id"]:
                return jsonify({"error": "Selected room is full."}), 400

        conn.execute("""
            UPDATE students SET name=?, email=?, phone=?, course=?, year=?, room_id=?
            WHERE id=?
        """, (data["name"], data["email"], data["phone"], data["course"],
              data["year"], new_room, student_id))

        if old["room_id"] != new_room:
            if old["room_id"]:
                conn.execute("UPDATE rooms SET occupied=MAX(occupied-1,0) WHERE id=?", (old["room_id"],))
            if new_room:
                conn.execute("UPDATE rooms SET occupied=occupied+1 WHERE id=?", (new_room,))
        conn.commit()
        return jsonify({"message": "Student updated successfully."})
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    conn = get_db()
    row = conn.execute("SELECT room_id FROM students WHERE id=?", (student_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Student not found."}), 404
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    if row["room_id"]:
        conn.execute("UPDATE rooms SET occupied=MAX(occupied-1,0) WHERE id=?", (row["room_id"],))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted successfully."})

@app.get("/api/rooms")
def get_rooms():
    conn = get_db()
    rows = conn.execute("SELECT *, capacity-occupied AS available FROM rooms ORDER BY room_number").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/rooms")
def add_room():
    data = request.get_json()
    try:
        conn = get_db()
        conn.execute("INSERT INTO rooms(room_number,block,floor,capacity,occupied,type) VALUES(?,?,?,?,?,?)",
                     (data["room_number"], data["block"], data["floor"], int(data["capacity"]), 0, data["type"]))
        conn.commit()
        conn.close()
        return jsonify({"message": "Room added successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.put("/api/rooms/<int:room_id>")
def update_room(room_id):
    data = request.get_json()
    conn = get_db()
    room = conn.execute("SELECT occupied FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        conn.close()
        return jsonify({"error": "Room not found."}), 404
    capacity = int(data["capacity"])
    if capacity < room["occupied"]:
        conn.close()
        return jsonify({"error": f"Capacity cannot be less than occupied beds ({room['occupied']})."}), 400
    conn.execute("UPDATE rooms SET room_number=?,block=?,floor=?,capacity=?,type=? WHERE id=?",
                 (data["room_number"], data["block"], data["floor"], capacity, data["type"], room_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Room updated successfully."})

@app.delete("/api/rooms/<int:room_id>")
def delete_room(room_id):
    conn = get_db()
    room = conn.execute("SELECT occupied FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        conn.close()
        return jsonify({"error": "Room not found."}), 404
    if room["occupied"] > 0:
        conn.close()
        return jsonify({"error": "Cannot delete an occupied room."}), 400
    conn.execute("DELETE FROM rooms WHERE id=?", (room_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Room deleted successfully."})

@app.get("/api/staff")
def get_staff():
    conn = get_db()
    rows = conn.execute("SELECT * FROM staff ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/staff")
def add_staff():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO staff(name,role,phone,email,shift) VALUES(?,?,?,?,?)",
                 (data["name"], data["role"], data["phone"], data["email"], data["shift"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Staff member added."}), 201

@app.delete("/api/staff/<int:staff_id>")
def delete_staff(staff_id):
    conn = get_db()
    conn.execute("DELETE FROM staff WHERE id=?", (staff_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Staff member deleted."})

@app.get("/api/fees")
def get_fees():
    conn = get_db()
    rows = conn.execute("""
        SELECT f.*, s.name student_name
        FROM fees f JOIN students s ON f.student_id=s.id
        ORDER BY f.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/fees")
def add_fee():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO fees(student_id,amount,due_date,paid_date,status,description) VALUES(?,?,?,?,?,?)",
                 (data["student_id"], float(data["amount"]), data["due_date"],
                  data.get("paid_date") or None, data["status"], data.get("description","")))
    conn.commit()
    conn.close()
    return jsonify({"message": "Fee record added."}), 201

@app.put("/api/fees/<int:fee_id>")
def update_fee(fee_id):
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE fees SET amount=?,due_date=?,paid_date=?,status=?,description=? WHERE id=?",
                 (float(data["amount"]), data["due_date"], data.get("paid_date") or None,
                  data["status"], data.get("description",""), fee_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Fee updated."})

@app.get("/api/complaints")
def get_complaints():
    conn = get_db()
    rows = conn.execute("""
        SELECT c.*, s.name student_name
        FROM complaints c JOIN students s ON c.student_id=s.id
        ORDER BY c.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.post("/api/complaints")
def add_complaint():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO complaints(student_id,title,description,status,created_at) VALUES(?,?,?,?,datetime('now'))",
                 (data["student_id"], data["title"], data["description"], data.get("status","Pending")))
    conn.commit()
    conn.close()
    return jsonify({"message": "Complaint submitted."}), 201

@app.put("/api/complaints/<int:complaint_id>")
def update_complaint(complaint_id):
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE complaints SET status=? WHERE id=?", (data["status"], complaint_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Complaint status updated."})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
