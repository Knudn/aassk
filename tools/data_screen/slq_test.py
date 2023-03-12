import sqlite3
con = sqlite3.connect("test.db")
cur = con.cursor()

cur.execute("DROP TABLE active_drivers;")
cur.execute("CREATE TABLE active_drivers(driver, c_num)")

cur.execute("""
    INSERT INTO active_drivers VALUES
        ('Driver_1', 0),
        ('Driver_2', 0)
""")

cur.execute(""" UPDATE active_drivers
SET c_num = 55
WHERE driver = 'Driver_1';
""")

for row in cur.execute("SELECT * FROM active_drivers"):
    print(row)

cur.execute(""" UPDATE active_drivers
SET c_num = CASE
           WHEN driver = 'Driver_1' THEN 65
           WHEN driver = 'Driver_2' THEN 88
         END;
""")

for row in cur.execute("SELECT * FROM active_drivers"):
    print(row)