# Simple Password Manager Backend API

This is a simple Python-based backend API for a password manager. It provides basic functionality for user management and password storage. This README will guide you through the setup process and how to configure the necessary environment variables.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your system.
- [Pip](https://pip.pypa.io/en/stable/) installed for package management.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/Kalu548/password-manager-backend.git
   cd password-manager-backend
   ```

2. Create a virtual environment (recommended) to isolate dependencies:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before running the API, you need to configure the following environment variables in a `.env` file in the project directory:

```env
DB_HOST=""
DB_USER=""
DB_PASSWORD=""
DB_NAME=""
SECRET_KEY=""
```

Replace the empty strings (`""`) with your actual database details and a secret key for JWT token generation.

## Running the API

Once you have configured the environment variables, you can start the API. Make sure your virtual environment is activated, and you are in the project directory:

```bash
python app.py
```

The API will start running on `http://localhost:8000`. You can access the API using various API client tools like [Postman](https://www.postman.com/) or by integrating it into your frontend application.

## API Endpoints

This simple password manager backend API provides the following endpoints:

### User Signup

- **POST /user/signup:** Create a new user account.

### User Login

- **POST /user/login:** Authenticate and log in a user.

### Create Password

- **POST /password/create:** Create a new password entry.

### Get All Passwords

- **GET /password/all:** Get a list of all saved passwords.

### Delete Password

- **GET /password/delete/{pass_id}:** Delete a password entry by its ID.

### Get Password

- **GET /password/get/{pass_id}:** Get details of a specific password by its ID.

### Update Password

- **POST /password/update:** Update an existing password entry.

### Export All Passwords

- **GET /password/export_all:** Export all passwords to a CSV file.

Please note that proper authentication and authorization mechanisms should be implemented in a production environment to secure these endpoints.
## Security Note

Security is essential when handling passwords. Ensure that you follow best practices for securing your database and API, such as using strong encryption and authentication mechanisms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
