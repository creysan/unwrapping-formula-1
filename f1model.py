import fastf1
import fastf1.plotting

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

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
    combined_data = []
    for year in years:
        for race_name in race_names:
            race_data = get_race_data(year, race_name)
            qualifying_data = get_qualifying_data(year, race_name)
            
            if not race_data.empty and not qualifying_data.empty:
                # Merge race and qualifying data on common columns
                combined = pd.merge(race_data, 
                                    qualifying_data, 
                                    on = ['DriverId', 'Year', 'RaceName', 'DriverNumber', 'Abbreviation', 'FullName', 'TeamName', 'RaceName'], 
                                    how = 'inner')
                combined_data.append(combined)
            print("DONE GETTING RACE", race_name)
        print("Completed collecting race data for: ", year)
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was collected

def prepare_features(data):
    # Convert qualifying times (Q1_y, Q2_y, Q3_y) to seconds and fill NaNs with high values (indicating no time set)
    for session in ['Q1_y', 'Q2_y', 'Q3_y']:
        data[session] = pd.to_timedelta(data[session], errors='coerce').dt.total_seconds()
        data[session] = data[session].fillna(9999)
    
    # Encode categorical features
    data['DriverId'] = data['DriverId'].astype('category').cat.codes
    data['TeamName'] = data['TeamName'].astype('category').cat.codes
    
    # Feature for average qualifying time
    data['AvgQualifyingTime'] = data[['Q1_y', 'Q2_y', 'Q3_y']].mean(axis=1)
    
    return data


# Prepare features
prepared_data = prepare_features(df)

prepared_data['IsWinner'] = (prepared_data['Position'] == 1).astype(int)

# Filter out extreme values in AvgQualifyingTime
valid_data = prepared_data[prepared_data['AvgQualifyingTime'] < 9999]

# Handle NaNs in GridPosition (e.g., filling NaNs with median grid position)
valid_data['GridPosition'].fillna(valid_data['GridPosition'].median(), inplace=True)

# Define features and target
features = ['GridPosition', 'AvgQualifyingTime', 'Position']
X = valid_data[features]

# Fill NaNs in the 'Position' column with the mean of the column
X['Position'].fillna(X['Position'].mean(), inplace=True)

# Alternatively, you can use the median if it's more appropriate for your data:
# X['Position'].fillna(X['Position'].median(), inplace=True)

y = valid_data['IsWinner']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

# Train a Neural Network classifier
model = MLPClassifier(hidden_layer_sizes=(200, 200, 100), max_iter=1000, random_state=1)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(classification_report(y_test, y_pred))



from flask import jsonify  # Import necessary Flask modules

# Define your prediction function
def predict_race_winner(year, race_name):
    race_to_predict = collect_data([year], [race_name])

    # Prepare features for prediction
    prepared_target_data = prepare_features(race_to_predict)
    X_target_race = prepared_target_data[features]
    
    # Make predictions
    win_probabilities = model.predict_proba(X_target_race)[:, 1]
    prepared_target_data['WinProbability'] = win_probabilities
    
    # Sort by 'WinProbability' in descending order and get the top 5
    top_5_drivers = prepared_target_data.nlargest(5, 'WinProbability')
    
    return top_5_drivers


if __name__ == '__main__':
    # Code to run the script standalone for testing or training
    # Example: Collecting data and making a prediction for a specific race
    year = 2024
    race = 'Austria'

    # Make a prediction
    prediction_result = predict_race_winner(year, race)
    print(f"Prediction result for {race} in {year}:")
    print(prediction_result)