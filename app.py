import os
from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
from utils import (load_keywords, classify_sentiment, analyze_time_series, create_word_cloud, create_pie_chart, 
                   create_histogram, create_stacked_bar_chart, create_treemap_chart, get_most_published_headline, create_network_graph)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/start_here')
def start_here():
    return render_template('start_here.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join('uploads', file.filename)
        file.save(filepath)
        keyword = request.form.get('keyword')
        time_period = request.form.get('time_period')
        print(f'[UPLOAD] filepath: {filepath}, keyword: {keyword}, time_period: {time_period}')  # Debug print statement
        return redirect(url_for('news_explore', filepath=filepath, keyword=keyword, time_period=time_period))

@app.route('/news_explore')
def news_explore():
    filepath = request.args.get('filepath')
    keyword = request.args.get('keyword')
    time_period = request.args.get('time_period')
    print(f'[NEWS EXPLORE] filepath: {filepath}, keyword: {keyword}, time_period: {time_period}')  # Debug print statement

    df = pd.read_csv(filepath)

    custom_stopwords = load_keywords('C:/Users/colos/Desktop/KNA/custom_stopwords.txt')
    positive_keywords = load_keywords('C:/Users/colos/Desktop/KNA/positive.txt')
    negative_keywords = load_keywords('C:/Users/colos/Desktop/KNA/negative.txt')

    # Apply sentiment classification
    df['sentiment'] = df['description'].apply(lambda x: classify_sentiment(x, keyword, positive_keywords, negative_keywords))
    
    filtered_df = df[df['description'].str.contains(keyword, case=False, na=False) | df['title'].str.contains(keyword, case=False, na=False)]

    # Calculate sentiment volumes
    negative_volume = filtered_df[filtered_df['sentiment'] == 'negative'].shape[0]
    positive_volume = filtered_df[filtered_df['sentiment'] == 'positive'].shape[0]
    neutral_volume = filtered_df[filtered_df['sentiment'] == 'neutral'].shape[0]

    # Get the most published headline
    most_published_headline = get_most_published_headline(filtered_df)

    time_series, highest_volume_period, highest_volume_value, timeseries_image_path = analyze_time_series(filtered_df, keyword, time_period)
    wordcloud_image_path = create_word_cloud(filtered_df)
    pie_chart_path = create_pie_chart(filtered_df)
    histogram_path = create_histogram(filtered_df)
    stacked_bar_chart_path = create_stacked_bar_chart(filtered_df, time_period)
    treemap_chart_path = create_treemap_chart(filtered_df)

    # Create network graph
    network_graph_path, network_graph_thumbnail_path = create_network_graph(filtered_df, keyword)

    recent_news = filtered_df.head(20).to_dict(orient='records')  # Get the most recent 20 news articles as a list of dictionaries

    print(f'[NEWS EXPLORE] recent_news: {recent_news}')  # Debug print statement

    return render_template('news_explore.html', keyword=keyword, time_series=time_series, highest_volume_period=highest_volume_period,
                           highest_volume_value=highest_volume_value, total_stories=len(filtered_df), negative_volume=negative_volume,
                           positive_volume=positive_volume, neutral_volume=neutral_volume, pie_chart_path=pie_chart_path,
                           histogram_path=histogram_path, stacked_bar_chart_path=stacked_bar_chart_path, treemap_chart_path=treemap_chart_path,
                           wordcloud_image_path=wordcloud_image_path, timeseries_image_path=timeseries_image_path, recent_news=recent_news,
                           most_published_headline=most_published_headline, network_graph_path=network_graph_path, network_graph_thumbnail_path=network_graph_thumbnail_path)

if __name__ == '__main__':
    app.run(debug=True)
