# areruya_frank-21RP04953
work



This code is a Flask web application that provides basic user registration, login, and service ordering functionalities. It interacts with a MySQL database to store and retrieve user data, service information, and order details. Below is a breakdown of what each part of the code does and how it runs:

### Key Functionalities

1. **User Registration**:
   - Users can register by providing their first name, last name, phone number, username, and password.
   - Passwords are hashed before being stored in the database for security.

2. **User Login**:
   - Registered users can log in by providing their username and password.
   - The application checks the credentials against the hashed passwords stored in the database.

3. **Dashboard**:
   - Logged-in users can access a dashboard that displays their username.

4. **Service Ordering**:
   - Logged-in users can view available services and place orders by providing their details and selecting a service.
   - The order details are stored in the database.

5. **Logout**:
   - Users can log out, which clears their session.

### Code Components and Flow

1. **Database Connection**:
   - `get_db_connection()` function establishes a connection to the MySQL database.

2. **User Authentication**:
   - `register()` route handles user registration. It hashes the password and inserts user details into the database.
   - `login()` route handles user login. It verifies the username and password against the stored hashed password and initiates a session.

3. **Dashboard and Order Service**:
   - `dashboard()` route displays the user's dashboard if they are logged in.
   - `order_service()` route displays available services and allows logged-in users to place orders.

4. **Utility Functions**:
   - `fetch_user_from_session()`, `fetch_services_from_database()`, `get_service_price_from_database()`, and `insert_order_into_database()` handle database operations related to users and services.

5. **Session Management**:
   - `login_required()` decorator ensures that certain routes are accessible only to logged-in users.
   - `logout()` route clears the user's session, effectively logging them out.

### How the Application Runs

1. **Initialization**:
   - The application is initialized with `Flask(__name__)`.
   - `app.secret_key` is set for session management.

2. **Routes and Views**:
   - The application defines several routes (`/`, `/register`, `/login`, `/dashboard`, `/order_service`, `/logout`) that map to specific functions handling user interactions.

3. **Starting the Server**:
   - The application runs the server with `app.run(debug=True)`. When accessed via a web browser, users can navigate through the registration, login, and service ordering functionalities.

### Running the Application

To run this application, you need to have the necessary dependencies installed, including Flask and mysql-connector-python. Follow these steps:

1. **Install Dependencies**:
   ```sh
   pip install flask mysql-connector-python werkzeug
   ```

2. **Set Up the Database**:
   - Ensure you have a MySQL database set up with the required tables (`users`, `services`, `orders`).

3. **Run the Application**:
   ```sh
   python app.py
   ```

4. **Access the Application**:
   - Open a web browser and navigate to `http://localhost:5000` to access the application.

This setup will allow you to register users, log in, view the dashboard, and place service orders while interacting with the MySQL database for data storage and retrieval.
