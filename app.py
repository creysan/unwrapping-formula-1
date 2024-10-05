from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime
import fastf1
import os
import pandas as pd
import plotly.express as px
from model import predict_race_winner, load_model

load_dotenv()

app = Flask(__name__)

# Contact Form Email
app.config.update(
    DEBUG=True,
    MAIL_SERVER = os.getenv('MAIL_SERVER'), 
    MAIL_PORT = os.getenv('MAIL_PORT'),
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL'),
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
)

mail = Mail(app)

# Path to cache directory
CACHE_DIR = 'cache'

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)  # Enable caching

# Route for the Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the Calendar Page
@app.route('/calendar')
def calendar():
    # Get the current year
    current_year = datetime.now().year
    
    # Get the event schedule for the current year
    events = fastf1.get_event_schedule(current_year)
    
    current_date = datetime.now()

    # Lists to hold categorized races
    past_races = []
    upcoming_races = []
    current_race = None

    for index, event in events.iterrows():
        race_date = event['EventDate']  # Directly use Timestamp
        race_info = {
            'round': event['RoundNumber'],
            'name': event['EventName'],
            'location': event['Location'],
            'date': race_date.strftime('%B %d, %Y'),  # Format the date for display
            'country': event['Country'].lower()
        }
        
        if race_date.date() == current_date.date():
            current_race = race_info
        elif race_date < current_date:
            past_races.append(race_info)
        else:
            upcoming_races.append(race_info)
    return render_template('calendar.html', 
                           current_race=current_race,
                           past_races=past_races,
                           upcoming_races=upcoming_races)

# Route for the data page
@app.route('/unwrap')
def unwrap():
    return render_template('unwrap.html')

# Route for the news page
@app.route('/news')
def news():
    return render_template('news.html')

# Route for the learn page
@app.route('/learn')
def learn():
    return render_template('learn.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# METHODS
@app.route('/get_years', methods=['GET'])
def get_years():
    # List of available years for F1 seasons in descending order
    available_years = list(range(2024, 1949, -1))
    return jsonify(available_years)

@app.route('/get_events', methods=['GET'])
def get_events():
    race_year = request.args.get('year', default=2023, type=int)
    events = fastf1.get_event_schedule(race_year)
    
    event_list = []
    for index, event in events.iterrows():
        event_list.append({
            'round': event['RoundNumber'],
            'name': event['EventName']
        })
    
    return jsonify(event_list)

@app.route('/get_drivers', methods=['GET'])
def get_drivers():
    year = request.args.get('year')
    race_round = request.args.get('round')

    try:
        session = fastf1.get_session(int(year), int(race_round), 'R')  # 'R' for Race
        session.load()

        # Access session results to get driver information
        session_results = session.results
        
        drivers = []
        for index, driver in session_results.iterrows():
            driver_info = {
                'driverId': driver['DriverId'],
                'driverName': driver['FullName'],
                'driverAbbreviation': driver['Abbreviation']
                # Add more attributes as needed
            }
            drivers.append(driver_info)

        return jsonify(drivers)
    
    except Exception as e:
        error_msg = f"Error fetching drivers for {year} round {race_round}: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500  # Return error message with status code 500

@app.route('/get_race_data', methods=['GET'])
def get_race_data():
    year = request.args.get('year', default=2023, type=int)
    race_round = request.args.get('round', default=1, type=int)
    driver_id = request.args.get('drivers')  # Get selected driver ID

    session = fastf1.get_session(year, race_round, 'R')  # 'R' for Race
    session.load()

    # Convert Race Round to Event Name
    event_names = fastf1.get_event_schedule(year)
    round_name = event_names.loc[event_names['RoundNumber'] == race_round, 'EventName'].values[0]

    # Convert driver_id to full name
    session_results = session.results
    fullDriverName = next(driver['FullName'] for _, driver in session_results.iterrows() if driver['Abbreviation'] == driver_id)

    # Filter session results for the selected driver
    laps_data = session.laps.pick_drivers(driver_id)

    if len(laps_data) == 0:
        return jsonify({'error': f'No data found for driver {driver_id} in {year} round {race_round}'}), 404

    # Retrieve lap numbers and lap times
    lap_numbers = laps_data['LapNumber']
    lap_times = laps_data['LapTime']
    lap_times_seconds = lap_times.dt.total_seconds()  # Convert lap times to seconds for plotting

    # Create a DataFrame for Plotly
    df = pd.DataFrame({
        'Lap Number': lap_numbers,
        'Lap Time (seconds)': lap_times_seconds
    })

    # Create an interactive plot using Plotly
    fig = px.line(df, x='Lap Number', y='Lap Time (seconds)', title=f'Lap Times for {fullDriverName} in {year}\'s {round_name}')
    fig.update_traces(mode='lines+markers', hovertemplate='Lap: %{x}<br>Time: %{y:.2f} seconds')

    # Convert plot to JSON for rendering in the front-end
    graphJSON = fig.to_json()

    # Prepare response data
    response_data = {
        'plotly_json': graphJSON,
        'exceptional_laps': {},  # Placeholder for additional data if needed
    }

    return jsonify(response_data)


@app.route('/seconds_to_minutes', methods=['GET'])
def seconds_to_minutes(seconds):
    """
    Convert seconds to a string in the format 'MM:SS'.
    
    Parameters:
    seconds (float): The time in seconds.
    
    Returns:
    str: The time in 'MM:SS' format.
    """
    minutes = int(seconds // 60)  # Find the number of whole minutes
    remaining_seconds = int(seconds % 60)  # Find the remaining seconds

    # Format the output as 'MM:SS' with leading zeros for single-digit minutes and seconds
    return f"{minutes:02}:{remaining_seconds:02}"
        
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    userMessage = request.form.get('message')
    msg = Message(
       subject='Hello ' + name,
       sender = email,
       recipients= ['christian7reyes@gmail.com'],
       body = f"Message:\n{userMessage}"
    )
    mail.send(msg)
    return jsonify({'success': True, 'message': 'Message sent successfully!'})


@app.route('/predict_winner', methods=['POST'])
def predict_winner():
    data = request.json
    year = data.get('year')
    event_round = data.get('event')
    
    if not year or not event_round:
        return jsonify({'error': "Year and event round are required"}), 400
    
    try:
        year = int(year)
        event_round = int(event_round)
    except ValueError:
        return jsonify({'error': "Year and event round must be valid integers"}), 400

    try:
        # Find the event name corresponding to the given round number
        event_names = fastf1.get_event_schedule(year)

        if event_round not in event_names['RoundNumber'].values:
            return jsonify({'error': f"Event round {event_round} not found for year {year}"}), 404
        round_name = event_names.loc[event_names['RoundNumber'] == event_round, 'Country'].values[0]

        # Load the pre-trained model
        loaded_model = load_model('pretrained_race_winner_model.pkl')

        # Define the features needed for prediction
        features = ['GridPosition', 'AvgQualifyingTime', 'Position']

        # Call predict_race_winner with the loaded model and features
        prediction_result = predict_race_winner(year, round_name, loaded_model, features)

        return jsonify({'predicted_winners': prediction_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)