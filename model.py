import fastf1
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from flask import jsonify
import joblib  # Import for saving/loading models

# Load data globally or in a main function
df = pd.read_csv('racing-data.csv')

def get_race_data(year, race_name, session_type="R"):
    try:
        session = fastf1.get_session(year, race_name, session_type)
        session.load()
        race_data = session.results.loc[:, [
            'DriverNumber', 'DriverId', 'Abbreviation', 'FullName',
            'TeamName', 'Position', 'GridPosition', 'Q1', 'Q2', 'Q3'
        ]]
        race_data['Year'] = year
        race_data['RaceName'] = race_name
        return race_data
    except Exception as e:
        print(f"Error loading data for {race_name} in {year}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

def get_qualifying_data(year, race_name, session_type="Q"):
    try:
        session = fastf1.get_session(year, race_name, session_type)
        session.load()
        qualifying_data = session.results.loc[:, [
            'DriverNumber', 'DriverId', 'Abbreviation', 'FullName',
            'TeamName', 'Q1', 'Q2', 'Q3'
        ]]
        qualifying_data['Year'] = year
        qualifying_data['RaceName'] = race_name
        return qualifying_data
    except Exception as e:
        print(f"Error loading data for {race_name} in {year}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

def collect_data(years, race_names):
    """
    Collect and merge race and qualifying data for multiple years and races.
    """
    combined_data = []
    for year in years:
        for race_name in race_names:
            race_data = get_race_data(year, race_name)
            qualifying_data = get_qualifying_data(year, race_name)
            
            if not race_data.empty and not qualifying_data.empty:
                # Merge race and qualifying data on common columns
                combined = pd.merge(
                    race_data, qualifying_data,
                    on=['DriverId', 'Year', 'RaceName', 'DriverNumber', 'Abbreviation', 'FullName', 'TeamName'],
                    how='inner'
                )
                combined_data.append(combined)
            print(f"Collected data for {race_name} in {year}")
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was collected

def prepare_features(data):
    """
    Prepare and preprocess data features.
    """
    # Convert qualifying times (Q1_y, Q2_y, Q3_y) to seconds and fill NaNs with high values
    for session in ['Q1_y', 'Q2_y', 'Q3_y']:
        data[session] = pd.to_timedelta(data[session], errors='coerce').dt.total_seconds()
        data[session] = data[session].fillna(9999)
    
    # Encode categorical features
    data['DriverId'] = data['DriverId'].astype('category').cat.codes
    data['TeamName'] = data['TeamName'].astype('category').cat.codes
    
    # Feature for average qualifying time
    data['AvgQualifyingTime'] = data[['Q1_y', 'Q2_y', 'Q3_y']].mean(axis=1)
    
    return data

def handle_missing_values(data):
    """
    Handle missing values in the dataset systematically.
    """
    data = data.copy()  # Avoid changing the original DataFrame
    # Fill NaNs in GridPosition with the median grid position
    data['GridPosition'].fillna(data['GridPosition'].median(), inplace=True)
    # Fill NaNs in the Position column with the mean of the column
    data['Position'].fillna(data['Position'].mean(), inplace=True)
    return data

def train_model(X_train, y_train):
    """
    Train the MLPClassifier model.
    """
    model = MLPClassifier(hidden_layer_sizes=(200, 200, 100), max_iter=1000, random_state=1)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model.
    """
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    return accuracy, report

def save_model(model, filename):
    """
    Save the trained model to disk.
    """
    joblib.dump(model, filename)
    print(f"Model saved to {filename}")

def load_model(filename):
    """
    Load a model from disk.
    """
    model = joblib.load(filename)
    print(f"Model loaded from {filename}")
    return model

def predict_race_winner(year, race_name, model, features):
    """
    Predict the winner for a given race.
    """
    race_to_predict = collect_data([year], [race_name])
    if race_to_predict.empty:
        print(f"No data available for {race_name} in {year}")
        return []

    # Prepare features for prediction
    prepared_target_data = prepare_features(race_to_predict)
    prepared_target_data = handle_missing_values(prepared_target_data)
    X_target_race = prepared_target_data[features]

    # Make predictions
    win_probabilities = model.predict_proba(X_target_race)[:, 1]
    prepared_target_data['WinProbability'] = win_probabilities

    # Sort by 'WinProbability' in descending order and get the top 5
    top_5_drivers = prepared_target_data.nlargest(5, 'WinProbability')

    # Convert the top 5 drivers' names to a list
    predicted_winners = top_5_drivers['FullName'].tolist()

    return predicted_winners


if __name__ == '__main__':
    # Step 1: Prepare and preprocess data
    prepared_data = prepare_features(df)
    prepared_data = handle_missing_values(prepared_data)
    prepared_data['IsWinner'] = (prepared_data['Position'] == 1).astype(int)

    # Filter out extreme values in AvgQualifyingTime
    valid_data = prepared_data[prepared_data['AvgQualifyingTime'] < 9999]

    # Define features and target
    features = ['GridPosition', 'AvgQualifyingTime', 'Position']
    X = valid_data[features]
    y = valid_data['IsWinner']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

    # Step 2: Train and evaluate the model
    model = train_model(X_train, y_train)
    accuracy, report = evaluate_model(model, X_test, y_test)
    
    print(f"Model Accuracy: {accuracy:.3f}")
    print("Classification Report:")
    print(report)

    # Step 3: Save the trained model
    save_model(model, 'pretrained_race_winner_model.pkl')
