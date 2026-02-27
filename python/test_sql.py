import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=SqlAiDatathon;"
    "UID=sa;"
    "PWD=4taqila4;"
    "Encrypt=yes;TrustServerCertificate=yes;"
)

print("Connected!")
conn.close()