# Korean News Analysis Web App

This web app helps users understand news trends based on CSV files of uploaded news datasets that are selectively collected and processed.

## Project Structure
KNA
├── templates
│ ├── base.html
│ ├── landing_page.html
│ ├── start_here.html
│ ├── news_explore.html
│ ├── summary_export.html
│ └── error.html
├── static
│ ├── css
│ │ └── styles.css
│ └── uploads # This should contain the generated images
├── uploads # This should contain uploaded and processed files
├── app.py
├── utils.py
├── custom_stopwords.txt
├── KOSPI200_Industry_Info.xlsx
├── positive.txt
├── negative.txt
├── requirements.txt
├── sample.csv
├── LICENSE
└── venv # Your virtual environment directory


## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/cmoon78/korean-news-analysis.git
    cd korean-news-analysis
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the App

1. **Activate the virtual environment if not already activated:**

    ```bash
    venv\Scripts\activate
    ```

2. **Run the application:**

    ```bash
    python app.py
    ```

3. **Access the app:**

    Open a web browser and go to `http://localhost:8080`.

## Features

- **Upload News Datasets**: Users can upload CSV files containing news data. The app supports various formats and ensures data integrity before processing.
- **Analyze Trends**: The app processes the data and helps users understand trends in the news. It performs sentiment analysis, keyword extraction, and frequency analysis to provide insights.
- **Explore News**: Users can explore the news data through an interactive web interface. The interface includes visualizations like charts and graphs to depict trends over time.
- **Generate Summaries**: The app can generate concise summaries of the news articles, highlighting the most important points.
- **Export Analysis**: Users can export the analysis results and summaries in various formats for further use.

## File Descriptions

- **app.py**: The main application file that runs the Flask web server.
- **utils.py**: Utility functions used by the application.
- **templates/**: HTML templates for the web pages.
- **static/**: Static files (CSS) used by the HTML templates.
- **uploads/**: Directory where uploaded files are stored.
- **KOSPI200_Industry_Info.xlsx**: Contains industry information related to the KOSPI 200 index.
- **custom_stopwords.txt**: Custom stopwords used for text analysis.
- **positive.txt**: List of positive words for sentiment analysis.
- **negative.txt**: List of negative words for sentiment analysis.
- **requirements.txt**: List of Python packages required to run the app.
- **sample.csv**: A sample CSV file for testing the application.
- **venv/**: Virtual environment directory (not included in the repository).

## Contribution

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

