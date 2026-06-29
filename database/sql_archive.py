import sqlite3

class sql_Memory():
    def __init__(self):
        
        # Connect directly to the database file (SQLite automatically creates it if it doesn't exist)
        self.connection = sqlite3.connect("security_archive.db",check_same_thread=False)

        #Create a cursor object
        self.cursor = self.connection.cursor()

        #when class intialize the table sets up it..
        self._initialize_table()
    
    def _initialize_table(self):
        # Use your cursor to execute a raw SQL command to set up your Excel-style table columns
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                incident_log TEXT,
                threat_score REAL,
                security_status TEXT
            )
        """)
        self.connection.commit()
        print("Relational SQL Database archive connected and verified!")

    def save_alert(self, ip: str, log: str, score: float, status: str):
        # a method we can call from main.py to insert rows into our table
        self.cursor.execute(
            "INSERT INTO security_alerts (ip_address, incident_log, threat_score, security_status) VALUES (?, ?, ?, ?)",
            (str(ip), str(log), float(score), str(status))
        )
        self.connection.commit()
        print(f"Alert successfully logged to SQL file for IP: {ip}")
