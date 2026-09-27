import psycopg2
from getpass import getpass


connection = psycopg2.connect(
    host="localhost",
    port=5432,
    database="cyberguard_dw",
    user="postgres",
    password=getpass("Enter PostgreSQL password: ")
)


print("POSTGRESQL CONNECTION SUCCESSFUL")


connection.close()