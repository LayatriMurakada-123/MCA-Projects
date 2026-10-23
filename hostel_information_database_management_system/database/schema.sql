CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT NOT NULL UNIQUE,
    block TEXT NOT NULL,
    floor INTEGER NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity > 0),
    occupied INTEGER NOT NULL DEFAULT 0 CHECK(occupied >= 0),
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    course TEXT NOT NULL,
    year TEXT NOT NULL,
    room_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    shift TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount >= 0),
    due_date TEXT NOT NULL,
    paid_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('Paid','Pending','Partial')),
    description TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Pending','In Progress','Resolved')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO rooms(room_number,block,floor,capacity,occupied,type) VALUES
('A-101','A',1,4,0,'4 Sharing'),
('A-102','A',1,4,0,'4 Sharing'),
('A-201','A',2,2,0,'2 Sharing'),
('B-101','B',1,3,0,'3 Sharing'),
('B-201','B',2,2,0,'2 Sharing');

INSERT OR IGNORE INTO staff(name,role,phone,email,shift) VALUES
('Ravi Kumar','Warden','9876543210','ravi@hostel.local','Morning'),
('Priya Sharma','Supervisor','9876543211','priya@hostel.local','Evening'),
('Suresh Rao','Security','9876543212','suresh@hostel.local','Night');

INSERT OR IGNORE INTO students(name,email,phone,course,year,room_id) VALUES
('Anjali Reddy','anjali@example.com','9000000001','MCA','2nd Year',1),
('Rahul Kumar','rahul@example.com','9000000002','MCA','1st Year',1),
('Sneha Devi','sneha@example.com','9000000003','MCA','2nd Year',2);

INSERT OR IGNORE INTO fees(student_id,amount,due_date,paid_date,status,description) VALUES
(1,8500,'2026-09-10','2026-09-02','Paid','September hostel fee'),
(2,8500,'2026-09-10',NULL,'Pending','September hostel fee'),
(3,8500,'2026-09-10',NULL,'Pending','September hostel fee');

INSERT OR IGNORE INTO complaints(student_id,title,description,status) VALUES
(1,'Fan not working','Ceiling fan needs repair.','Pending'),
(2,'Water issue','Hot water is not available.','In Progress');
