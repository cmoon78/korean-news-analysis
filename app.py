import pandas as pd
from flask import Flask, request, render_template, send_file, session, redirect, url_for
import os
import traceback
from flask_session import Session
from utils import (validate_csv, create_news_volume_graph, create_word_cloud, create_network_graph,
                   create_keyword_summary, prepare_filtered_news_data, get_total_stories,
                   get_highest_volume_date, get_most_published_headline, sentiment_analysis)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/start_here', methods=['GET'])
def start_here():
    return render_template('start_here.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file and file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            session['file_path'] = file_path
        else:
            return redirect(url_for('start_here'))

        keyword = request.form['keyword']
        report_type = request.form['report_type']
        time_filter = request.form['time_filter']
        if time_filter == 'monthly':
            time_filter = 'M'
        elif time_filter == 'yearly':
            time_filter = 'Y'
        df = pd.read_csv(file_path)
        
        # Filter by keyword
        filtered_df = df[df['title'].str.contains(keyword, na=False)]
        session['filtered_df'] = filtered_df.to_json(orient='split')  # Store filtered data in session

        validate_csv(filtered_df)
        create_news_volume_graph(filtered_df, time_filter)
        create_word_cloud(filtered_df)
        create_network_graph(filtered_df, keyword)
        create_keyword_summary(filtered_df)

        total_stories, total_filtered_stories = get_total_stories(df, filtered_df)
        highest_volume_date, highest_volume_count = get_highest_volume_date(filtered_df)
        most_published_headline, headline_count, headline_link = get_most_published_headline(filtered_df)
        positive_count, negative_count, positive_example, negative_example = sentiment_analysis(filtered_df)

        news_data = prepare_filtered_news_data(filtered_df)
        session['news_data'] = news_data  # Store news data in session for later use

        return render_template('news_explore.html', report_type=report_type, keyword_summary=open('static/keyword_summary.txt', encoding='utf-8').read(),
                               total_stories=total_stories, total_filtered_stories=total_filtered_stories, highest_volume_date=highest_volume_date,
                               highest_volume_count=highest_volume_count, most_published_headline=most_published_headline, headline_count=headline_count,
                               headline_link=headline_link, positive_count=positive_count, negative_count=negative_count, positive_example=positive_example,
                               negative_example=negative_example, news_data=news_data)
    except Exception as e:
        error_message = f"Failed to process file: {str(e)}\n{traceback.format_exc()}"
        return render_template('error.html', error_message=error_message), 500

@app.route('/news_explore')
def news_explore():
    try:
        filtered_df_json = session.get('filtered_df')
        news_data = session.get('news_data')
        if not filtered_df_json or not news_data:
            return redirect(url_for('start_here'))

        filtered_df = pd.read_json(filtered_df_json, orient='split')
        keyword_summary = open('static/keyword_summary.txt', encoding='utf-8').read()
        return render_template('news_explore.html', keyword_summary=keyword_summary, news_data=news_data)
    except Exception as e:
        error_message = f"Failed to load news data: {str(e)}\n{traceback.format_exc()}"
        return render_template('error.html', error_message=error_message), 500

@app.route('/summary_export')
def summary_export():
    return render_template('summary_export.html')

@app.route('/export', methods=['POST'])
def export_file():
    try:
        filtered_df_json = session.get('filtered_df')
        if not filtered_df_json:
            return redirect(url_for('start_here'))

        filtered_df = pd.read_json(filtered_df_json, orient='split')
        filtered_df = filtered_df[['pub_date', 'title', 'link']].sort_values(by='pub_date')
        file_format = request.form.get('report_type')
        if file_format == 'csv':
            output = 'filtered_news.csv'
            filtered_df.to_csv(output, index=False)
        else:
            output = 'filtered_news.xlsx'
            filtered_df.to_excel(output, index=False)
        return send_file(output, as_attachment=True)
    except Exception as e:
        error_message = f"Failed to export file: {str(e)}\n{traceback.format_exc()}"
        return render_template('error.html', error_message=error_message), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
