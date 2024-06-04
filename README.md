# Korean News Analysis Web App

This web app helps users understand news trends based on CSV files of uploaded news datasets that are selectively collected and processed.

# Caution
Before running the application, please be aware of the following:

1. **File Directory Update**: After downloading the repository, you'll need to update the file paths within the application code to reflect the location where you store your project folter on your local PC.

2. **CSV File Format**: The uploaded CSV file must contain specific columns for the application to process the data correctly. These columns are:
item_id | title | description | pub_date | author | link | category1 | category2 (optional) | source_name

If you want to use csv files with different data columns, you need to update app.py and utils.py to successfully run the code. 

## Project Structure
```
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
├── Sample_for_testing.csv
├── LICENSE
└── venv # Your virtual environment director
```
## Features
- **Upload and Analyze News Data**: Upload CSV files containing news articles and gain insights through keyword analysis, sentiment analysis, and company identification.
- **Keyword Filtering**: Filter news articles based on keywords within the description column to focus your analysis.
- **Data Visualization**: Explore news trends through various charts and graphs in the News Explore section, including total stories, volume by date, most published headlines, time series analysis, and sentiment over time.
- **Sentiment Analysis**: Gauge the overall sentiment (positive, negative, or neutral) of news articles based on keywords entered by the user and sentiment lexicons (positive.txt and negative.txt).
- **Company Identification**: Identify important companies mentioned in news articles using the KOSPI200_Industry_Info.xlsx file. This ensures accurate company recognition, even for similar names like "삼성" and "삼성전자".

## Data Description
CSV File Columns:
- **item_id**: A unique identifier for each news item.
- **title**: The headline of the news article.
- **description**: A brief description or excerpt from the news article.
- **pub_date**: The publication date of the news article.
- **author**: The author of the news article (if available).
- **link**: A URL link to the full news article.
- **category1**: The primary category of the news article.
- **category2**: The secondary category (may be empty).
- **source_name**: The source from which the news article was obtained.

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
    Upload Sample_for_testing.csv to check if the app is working correctly.



## File Descriptions

- **app.py**: The main application file that runs the Flask web server.
- **utils.py**: Utility functions used by the application.
- **templates/**: HTML templates for the web pages.
- **static/**: Static files (CSS) used by the HTML templates.
- **uploads/**: Directory where uploaded files are stored.
- **KOSPI200_Industry_Info.xlsx**: An Excel file used to identify important companies mentioned in the news.
- **custom_stopwords.txt**: Contains words to exclude during text processing, improving keyword analysis accuracy.
- **positive.txt**: Lists of positive words used to determine the sentiment of news articles relative to the user-specified keyword.
- **negative.txt**: List of negative words used to determine the sentiment of news articles relative to the user-specified keyword.
- **requirements.txt**: List of Python packages required to run the app.
- **Sample_for_testing.csv**: A sample CSV file for testing the application.
- **venv/**: Virtual environment directory (not included in the repository).

## Contribution

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

