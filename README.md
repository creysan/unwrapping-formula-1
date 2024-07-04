### README

# Formula 1 Race Data Visualizer

## Description

The Formula 1 Race Data Visualizer is a web application that allows users to explore and visualize race data from past Formula 1 races. Leveraging the FastF1 library, this application provides insights into average lap times and the fastest laps for selected races. Users can choose a race year and round, and the application will generate a plot displaying the average lap times per lap. Additionally, it highlights the driver with the fastest lap and their lap time.

## Features

- Select a specific Formula 1 race by year and round.
- Visualize the average lap times per lap in a race.
- Identify and display the driver with the fastest lap and their lap time.
- Easy-to-use web interface.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/f1-race-data-visualizer.git
   cd f1-race-data-visualizer
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python app.py
   ```

5. Open your web browser and go to `http://127.0.0.1:5000/` to access the application.

## Usage

1. On the main page, select the year and round of the Formula 1 race you are interested in.
2. Click the "Get Race Data" button to generate the visualization.
3. View the plot of average lap times per lap and information about the fastest lap.

## Dependencies

- Flask
- FastF1
- Matplotlib
- Pandas
- Base64
- OS
- IO

## Project Structure

```
f1-race-data-visualizer/
│
├── cache/                   # Directory for cached data
├── templates/
│   └── index.html           # HTML file for the web interface
├── app.py                   # Main application file
├── requirements.txt         # List of required Python packages
└── README.md                # Project README file
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.