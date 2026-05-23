import os

SERVER_NAME = os.getenv("DB_SERVER", r"(localdb)\MSSQLLocalDB")
DATABASE_NAME = os.getenv("DB_NAME", "DataQualityDB")