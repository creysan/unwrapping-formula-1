# Unwrapping Formula 1

## Project Overview

Unwrapping Formula 1 is a web application that provides Formula 1 race predictions and insights using machine learning. The application features a race calendar, detailed race analysis, and a prediction model for upcoming races.

## Features

- Interactive race calendar
- Race winner prediction model
- Detailed race analysis with lap time visualizations
- Dark mode support
- Responsive design for various devices

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Machine Learning: XGBoost (Gradient Boosting Classifier)
- Data Visualization: Plotly
- Additional Libraries: pandas, numpy, scikit-learn

## Machine Learning Model

Our Formula 1 race winner prediction model uses a Gradient Boosting Classifier (XGBoost) trained on historical F1 data from 2014 to 2023. 

Key aspects of the model:
- Data sources: race results, qualifying results, driver standings, and constructor standings
- Feature engineering: includes recent form, qualifying position, historical track performance, and current season performance
- Preprocessing: handling missing values, encoding categorical variables, and normalizing numerical features
- Model training: 80% training data, 20% test data, with 5-fold cross-validation
- Hyperparameter tuning: performed using grid search

Model performance:
- Accuracy on test set: 92%
- Key metrics: F1-score, ROC-AUC

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/unwrapping-formula-1.git
   cd unwrapping-formula-1
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   MAIL_SERVER=your_mail_server
   MAIL_PORT=your_mail_port
   MAIL_USE_SSL=True
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

6. Open a web browser and navigate to `http://localhost:5000`

## Usage

- Navigate through the site using the menu bar
- Use the calendar page to view upcoming and past races
- On the prediction page, select a year and event to get race winner predictions
- Toggle between light and dark mode using the switch in the navigation bar

## Contributing

Contributions to Unwrapping Formula 1 are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Formula 1 for the inspiration and data
- The FastF1 library for providing access to Formula 1 data
