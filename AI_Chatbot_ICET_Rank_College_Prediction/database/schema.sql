CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    university TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    category TEXT NOT NULL,
    course TEXT NOT NULL,
    cutoff_rank INTEGER NOT NULL,
    annual_fee REAL NOT NULL,
    website TEXT
);

INSERT OR IGNORE INTO colleges
(id,name,university,city,region,category,course,cutoff_rank,annual_fee,website) VALUES
(1,'Kakatiya Institute of Technology and Management','Kakatiya University','Warangal','AU','OC','MBA',3500,52000,'https://example.com'),
(2,'University College of Commerce & Business Management','Kakatiya University','Warangal','AU','OC','MBA',7000,35000,'https://example.com'),
(3,'Andhra University College of Engineering','Andhra University','Visakhapatnam','AU','OC','MBA',2500,60000,'https://example.com'),
(4,'Andhra University School of Management Studies','Andhra University','Visakhapatnam','AU','OC','MBA',5500,48000,'https://example.com'),
(5,'JNTU Kakinada School of Business Management','JNTU Kakinada','Kakinada','AU','OC','MBA',8000,55000,'https://example.com'),
(6,'JNTU Hyderabad School of Management Studies','JNTUH','Hyderabad','OU','OC','MBA',1800,65000,'https://example.com'),
(7,'Osmania University College of Commerce & Business Management','Osmania University','Hyderabad','OU','OC','MBA',3200,50000,'https://example.com'),
(8,'Nizam College','Osmania University','Hyderabad','OU','OC','MBA',9000,42000,'https://example.com'),
(9,'Kakatiya University Department of Computer Science','Kakatiya University','Warangal','AU','OC','MCA',4500,45000,'https://example.com'),
(10,'Andhra University Department of Computer Science','Andhra University','Visakhapatnam','AU','OC','MCA',3500,50000,'https://example.com'),
(11,'Osmania University Department of Computer Science','Osmania University','Hyderabad','OU','OC','MCA',3000,48000,'https://example.com'),
(12,'JNTU Hyderabad School of IT','JNTUH','Hyderabad','OU','OC','MCA',5000,58000,'https://example.com'),
(13,'Adikavi Nannaya University','AKNU','Rajamahendravaram','AU','OC','MBA',14000,38000,'https://example.com'),
(14,'Acharya Nagarjuna University','ANU','Guntur','AU','OC','MBA',12000,40000,'https://example.com'),
(15,'Sri Venkateswara University','SVU','Tirupati','AU','OC','MBA',10000,45000,'https://example.com'),
(16,'Dr. B.R. Ambedkar Open University','BRAOU','Hyderabad','OU','OC','MBA',25000,30000,'https://example.com');
