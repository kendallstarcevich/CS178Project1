import pymysql
import creds

try:
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db
    )
    print("✅ Connected to RDS MySQL!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
