import os

from google.cloud.sql.connector import Connector, IPTypes
import pymysql

import sqlalchemy
from sqlalchemy.sql import text
# Note: Make sure to set the environment variable GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "synerjix-sql-service-key.json"

def connect_with_connector_auto_iam_authn(instance_conn_name: str, user_name: str, db_name: str) -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector with Automatic IAM Database Authentication.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_iam_user = user_name

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(refresh_strategy="LAZY")

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_conn_name,
            "pymysql",
            user=db_iam_user,
            db=db_name,
            enable_iam_auth=True,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

    # Ensure the connector is closed when the engine is disposed
    pool.dispose = lambda: connector.close()

    return pool

if __name__ == "__main__":
    print("Connecting to Cloud SQL MySQL instance...")
    engine = connect_with_connector_auto_iam_authn(
        instance_conn_name="perfect-coil-448516-u5:us-west1:my-iam-mysql",
        user_name="mysql-service",
        db_name="test_synerjix"
    )
    if engine:
        print("Connection successful!")
        # engine.dispose()  # Ensure connections are closed on app shutdown
        with engine.connect() as connection:
            try:
                result = connection.execute(text("SELECT * FROM users;"))  # Wrap the query in text()
                for row in result:
                    print(row)  # Display each row in the result
                print("Inserting new user...")
                insert_query = text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)")
                connection.execute(insert_query, {
                    'username': "arijitde",
                    'email': "arijitde2050@gmal.com",
                    'password_hash': "abcd1234"
                })
                connection.commit()  # Commit the transaction
                print("User arijitde signed up successfully.")
            except Exception as e:
                print(f"An error occurred while fetching the data: {e}")

    else:
        print("Connection failed.")
