con = sqlite3.connect("test.db")
cur = con.cursor()
cur.execute("DROP TABLE active_drivers;")
cur.execute("CREATE TABLE active_drivers(driver, c_num)")

cur.execute("""
    INSERT INTO active_drivers VALUES
        ('Driver_1', 0),
        ('Driver_2', 0)
""")

cur.execute("CREATE TABLE start_list(c_num, first_name, last_name, snowmobile, club, time, finished,pair)")