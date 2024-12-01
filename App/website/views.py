import os
import time
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
import joblib
from werkzeug.security import generate_password_hash
from . import db  # Import db from your application
import pymysql  # Ensure pymysql is installed for MySQL connection
from datetime import datetime, timedelta
import mysql.connector
import pandas as pd
import threading
from sqlalchemy import create_engine

views = Blueprint('views', __name__)

# START OF CSV FILE FUNCTION

# Database connection details
db_config = {
    'host': 'localhost',
    'port': '3307',  # Use the correct port for your XAMPP MySQL setup
    'user': 'root',
    'password': '',  # Add your password if necessary
    'database': 'sensor_db'  # Replace with your database name
}

# Create SQLAlchemy engine
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

# CSV file path
csv_file_path = r'C:\DEMO PYTHON STRUCTURE\FLASK LOGIN PAGE SAMPLE3 - FORECASTING - Responsive - kapoy\data\data.csv'


# Function to map status string to integer
def status_to_int(status):
    if status == 'high':
        return 3
    elif status == 'moderate':
        return 2
    elif status == 'low':
        return 1
    else:
        return 0  # Fallback for unexpected values

try:
    # SQL query to retrieve data
    query = "SELECT distance, status, datetime, duration, fuel_consumed FROM data"  # Replace with your actual table name

    # Use Pandas to read the data using the SQLAlchemy engine
    df = pd.read_sql(query, engine)

    # Apply the status conversion to integers
    df['status'] = df['status'].apply(status_to_int)

    # Write the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print("Data exported to CSV successfully with status as integers.")

except Exception as e:  # Catch all exceptions
    print(f"An error occurred: {e}")

 # END OF CSV FILE FUNCTION


# Home route displaying the latest sensor reading
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # MySQL connection details
    db_host = 'localhost'
    db_user = 'root'
    db_password = ''  # Add your MySQL root password if set
    db_name = 'sensor_db'
    db_port = 3307  # Port you are using for MySQL

    latest_reading = None
    readings = []

    try:
        # Connect to MySQL database
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     port=db_port)
        cursor = connection.cursor()

        # Query to fetch the last distance and status
        query = "SELECT distance, status FROM data ORDER BY datetime DESC LIMIT 1"
        cursor.execute(query)
        latest_reading = cursor.fetchone()  # Fetch the latest reading

    except pymysql.MySQLError as e:
        flash(f"Database error: {str(e)}", category="error")
        latest_reading = None

    finally:
        if connection:
            connection.close()

    # Prepare distance and status for rendering
    distance = latest_reading[0] if latest_reading else None
    status = latest_reading[1] if latest_reading else None

    if request.method == 'POST':
        # Get the selected date range from the form
        date_range = request.form.get('date_range')

        # Custom range variables
        start_date = None
        end_date = None

        if date_range == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif date_range == 'last_7_days':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        elif date_range == 'last_month':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif date_range == 'custom':
            # Handle custom range
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            if start_date and end_date:
                # Convert start_date and end_date to datetime objects
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                flash('Please select both start and end dates for custom range.', category='error')
                return redirect(url_for('views.home'))

        # Fetch the data based on the selected date range
        if start_date and end_date:
            readings = get_historical_data(start_date, end_date)

    # Render home.html with the latest sensor reading and historical readings
    return render_template("home.html", user=current_user, distance=distance, status=status, readings=readings)


# Control panel route
@views.route('/controlPanel', methods=['GET', 'POST'])
@login_required
def control_panel():
    return render_template("controlPanel.html", user=current_user)


# Helper function to fetch historical data
def get_historical_data(start_date, end_date):
    # MySQL connection details
    db_host = 'localhost'
    db_user = 'root'
    db_password = ''  # Add your MySQL root password if set
    db_name = 'sensor_db'
    db_port = 3307  # Port you are using for MySQL

    try:
        # Connect to MySQL database
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     port=db_port)
        cursor = connection.cursor()

        # Query to fetch data within the specified date range
        query = "SELECT distance, status, datetime FROM data WHERE datetime BETWEEN %s AND %s ORDER BY datetime ASC"
        cursor.execute(query, (start_date, end_date))
        readings = cursor.fetchall()  # Fetch readings within the date range
        return readings

    except pymysql.MySQLError as e:
        flash(f"Database error: {str(e)}", category="error")
        return []

    finally:
        if connection:
            connection.close()


# New route to fetch distance data
@views.route('/distance', methods=['GET'])
@login_required
def get_distance():
    # MySQL connection details
    db_host = 'localhost'
    db_user = 'root'
    db_password = ''  # Add your MySQL root password if set
    db_name = 'sensor_db'
    db_port = 3307  # Port you are using for MySQL

    try:
        # Connect to MySQL database
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     port=db_port)
        cursor = connection.cursor()

        # Query to fetch the latest distance and status
        query = "SELECT distance, status FROM data ORDER BY datetime DESC LIMIT 1"
        cursor.execute(query)
        latest_reading = cursor.fetchone()

        # Query to fetch the last 10 readings
        query_last_ten = "SELECT distance, status, datetime FROM data ORDER BY datetime DESC LIMIT 10"
        cursor.execute(query_last_ten)
        last_readings = cursor.fetchall()

        if latest_reading:
            distance, status = latest_reading
            readings = [{'distance': r[0], 'status': r[1], 'datetime': r[2]} for r in last_readings]
            return jsonify({'distance': distance, 'status': status, 'readings': readings})
        else:
            return jsonify({'error': 'No data found'}), 404

    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if connection:
            connection.close()



# Function to check for distance threshold and trigger notifications
def check_for_notifications():
    # Define the threshold for triggering a notification
    low_distance_threshold = 150  # Adjust this value as per your requirement

    # MySQL connection details
    db_host = 'localhost'
    db_user = 'root'
    db_password = ''  # Add your MySQL root password if set
    db_name = 'sensor_db'
    db_port = 3307  # Port you are using for MySQL

    try:
        # Connect to MySQL database
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     port=db_port)
        cursor = connection.cursor()

        # Query to fetch the latest distance and status
        query = "SELECT distance, status FROM data ORDER BY datetime DESC LIMIT 1"

        cursor.execute(query)
        latest_reading = cursor.fetchone()
        

        if latest_reading:
            distance, status = latest_reading
            if distance < low_distance_threshold:
                # If the distance is below the threshold, return a notification
                return {
                    'message': f"Warning! Distance is low: {distance} cm.",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

        return None  # No notification

    except pymysql.MySQLError as e:
        flash(f"Database error: {str(e)}", category="error")
        return None

    finally:
        if connection:
            connection.close()

# Route to get notifications
@views.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    # Check for any notifications based on sensor data
    notification = check_for_notifications()
    if notification:
        return jsonify({'notification': notification}), 200
    else:
        return jsonify({'notification': None}), 200
    

 #CSV FILE FUNCTIONS

def update_csv():
    last_timestamp = None  # Variable to keep track of the last timestamp
    while True:  # Infinite loop to keep fetching data
        try:
            # Use pandas to read the data
            df = pd.read_sql("SELECT distance, status, datetime, duration, fuel_consumed FROM data", engine)

            # Convert status to integers
            df['status'] = df['status'].apply(status_to_int)

            # Check for the latest entry
            if not df.empty:
                latest_timestamp = df['datetime'].max()  # Get the most recent timestamp

                # If the latest timestamp is different from the last processed one
                if last_timestamp != latest_timestamp:
                    # Write the DataFrame to a CSV file
                    df.to_csv(csv_file_path, index=False)
                    last_timestamp = latest_timestamp  # Update the last timestamp
                    print("Data exported to CSV successfully with status as integers.")
                else:
                    print("No new data to export.")

            # Wait for a specific interval before fetching data again (e.g., every 5 seconds)
            time.sleep(5)  # Adjust the sleep time as needed

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait before trying again if there's an error

# Start the CSV updating function in a separate thread
csv_thread = threading.Thread(target=update_csv)
csv_thread.daemon = True  # This makes sure the thread will exit when the main program does
csv_thread.start()

# Settings route for user profile updates
@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        changes_made = False  # Track if changes were made

        # Check if email has changed
        if email and email != current_user.email:
            current_user.email = email
            changes_made = True

        # Check if first name has changed
        if first_name and first_name != current_user.first_name:
            current_user.first_name = first_name
            changes_made = True

        # Check if password is being updated
        if password1:
            if len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            elif password1 != password2:
                flash('Passwords do not match.', category='error')
            else:
                # If passwords match and are of sufficient length, update password
                current_user.password = generate_password_hash  (password1, method='sha256')
                changes_made = True

        # If changes were made, commit to the database and provide feedback
        if changes_made:
            try:
                db.session.commit()  # Commit changes to the database
                flash('Your information has been updated.', category='success')
            except Exception as e:
                flash(f"An error occurred while updating your information: {e}", category='error')
        else:
            flash('No changes made to your information.', category='info')

    return render_template('settings.html', user=current_user)



def generate_forecast_data(days=30, csv_file_path=r'C:\DEMO PYTHON STRUCTURE\FLASK LOGIN PAGE SAMPLE3 - FORECASTING - Responsive - kapoy\data\data.csv'):
    try:
        # Path to the new model pipeline
        new_model_path = r'C:\DEMO PYTHON STRUCTURE\FLASK LOGIN PAGE SAMPLE3 - FORECASTING - Responsive - kapoy\gradient_boosting_pipeline.pkl'
        
        # Check if the new model file exists
        if not os.path.exists(new_model_path):
            print("New model file not found!")
            return []

        # Load the new model
        model = joblib.load(new_model_path)
        print("New model loaded successfully.")

        # Load last known data
        if not os.path.exists(csv_file_path):
            print("CSV file not found!")
            return []

        last_data = pd.read_csv(csv_file_path)
        last_data['datetime'] = pd.to_datetime(last_data['datetime'])

        # Get the latest row to start future predictions from
        latest_row = last_data.iloc[-1].copy()

        # Select the necessary fields for the new model
        features = latest_row[['status', 'datetime', 'duration']].copy()

        # Convert datetime to UNIX timestamp for the model
        features['datetime'] = datetime.timestamp(features['datetime'])

        # Initialize predictions list
        predictions = []

        # Generate forward-looking predictions for each day
        for day in range(1, days + 1):
            # Predict based on current features
            predicted_value = model.predict(features.values.reshape(1, -1))
            predictions.append(predicted_value[0])

            # Prepare the features for the next day
            new_datetime = features['datetime'] + 86400  # Increment datetime by 1 day (86400 seconds)

            # Update features with the new future date
            features['datetime'] = new_datetime  # Update datetime to the next day

        # Format predictions as a list of dictionaries with date and prediction values
        prediction_dates = [(datetime.fromtimestamp(features['datetime'] - 86400 * (days - i))).strftime("%Y-%m-%d") for i in range(days)]
        result = [{"date": date, "prediction": float(pred)} for date, pred in zip(prediction_dates, predictions)]

        print("Forecast data generated successfully.")
        return result

    except Exception as e:
        print(f"Error generating forecast data: {e}")
        return []
    
     #Flask route to return forecast data
cached_forecast = {}  # Store results in memory
@views.route('/forecast', methods=['GET'])
def forecast():
    days = int(request.args.get('days', 7))
    if days in cached_forecast:
        return jsonify(cached_forecast[days])
    data = generate_forecast_data(days=days)
    cached_forecast[days] = data
    return jsonify(data)