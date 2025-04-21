# Flask App with Google Cloud MySQL and IAM Authentication

This project demonstrates a working example of a Flask web application that securely connects to Google Cloud MySQL using Google IAM service account authentication. The application implements a user authentication system with signup, login, and password management features, showcasing how to securely interact with Cloud SQL using IAM-based authentication.

## Features
- User authentication (signup, login, password management)
- Secure database connection using Google IAM service account
- SQLAlchemy integration with Cloud SQL
- Flask-based web interface

## Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account
- Google Cloud SQL MySQL instance
- IAM service account with appropriate permissions
- Service account key file (JSON)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd flask-gcp-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud credentials:
   - Place your service account key file (JSON) in the project root directory
   - Rename it to `synerjix-sql-service-key.json` or update the path in `gcp_mysql_connect.py`

5. Configure environment variables:
   - Set `GOOGLE_APPLICATION_CREDENTIALS` to point to your service account key file
   - Update the database connection details in `app.py`:
     - `instance_conn_name`
     - `user_name`
     - `db_name`

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Google IAM Service Account Integration

This project uses Google IAM service account authentication to securely connect to Cloud SQL MySQL. Here's how it works:

1. **Service Account Setup**:
   - A service account is created in Google Cloud IAM
   - The service account is granted appropriate roles (Cloud SQL Client, Cloud SQL Instance User)
   - A JSON key file is downloaded and used for authentication

2. **Authentication Flow**:
   - The application uses the Cloud SQL Python Connector with Automatic IAM Database Authentication
   - The service account credentials are automatically used to authenticate with Cloud SQL
   - No database passwords are stored in the application code
   - The connection is established using the service account's identity

3. **Security Benefits**:
   - No need to manage database passwords
   - Automatic credential rotation
   - Fine-grained access control through IAM roles
   - Secure connection using Google's infrastructure

The implementation can be found in `gcp_mysql_connect.py`, which sets up the connection pool using SQLAlchemy and the Cloud SQL Python Connector.
