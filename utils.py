import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for Matplotlib

import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter, defaultdict
import squarify
import networkx as nx
from PIL import Image
from kiwipiepy import Kiwi
from matplotlib.font_manager import FontProperties

# Define paths to resources
malgun_path = 'C:/Windows/Fonts/malgun.ttf'
custom_stopwords_path = 'C:/Users/colos/Desktop/KNA/custom_stopwords.txt'
important_companies_path = 'C:/Users/colos/Desktop/KNA/KOSPI200_Industry_Info.xlsx'

# Set font properties for matplotlib
font_prop = FontProperties(fname=malgun_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

kiwi = Kiwi()

def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        keywords = set(f.read().splitlines())
    return keywords

# Load custom stopwords
with open(custom_stopwords_path, 'r', encoding='utf-8') as f:
    custom_stopwords = set(f.read().splitlines())

# Load important companies from the Excel file
important_companies_df = pd.read_excel(important_companies_path)
important_companies = set(important_companies_df['Company_name'].dropna().tolist() + 
                          important_companies_df['Company_name2'].dropna().tolist())

def classify_sentiment(text, keyword, positive_keywords, negative_keywords):
    text = text.lower()
    positive_score = sum(1 for word in positive_keywords if word in text)
    negative_score = sum(1 for word in negative_keywords if word in text)
    if positive_score > negative_score:
        return 'positive'
    elif negative_score > positive_score:
        return 'negative'
    else:
        return 'neutral'

def analyze_time_series(df, keyword, time_period):
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    if time_period == 'year':
        df['time_period'] = df['pub_date'].dt.year
    elif time_period == 'month':
        df['time_period'] = df['pub_date'].dt.to_period('M')
    else:
        df['time_period'] = df['pub_date'].dt.date

    filtered_df = df[df['description'].str.contains(keyword, case=False, na=False)]
    time_series = filtered_df['time_period'].value_counts().sort_index()
    highest_volume_period = time_series.idxmax()
    highest_volume_value = time_series.max()

    plt.figure(figsize=(10, 5))
    colors = ['blue' if period != highest_volume_period else 'red' for period in time_series.index]
    bars = plt.bar(time_series.index.astype(str), time_series.values, color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{int(height)}', ha='center', va='bottom')

    plt.title(f'News Volume Over Time ({time_period.capitalize()})')
    plt.xlabel(time_period.capitalize())
    plt.ylabel('Number of News Articles')
    timeseries_image_path = os.path.join('static', 'uploads', 'timeseries.png')
    plt.tight_layout()
    plt.savefig(timeseries_image_path)
    plt.close()

    return time_series, highest_volume_period, highest_volume_value, timeseries_image_path

def normalize_text(text):
    particles = set(['은', '는', '이', '가', '를', '도', '랑', '을'])
    words = [word.form for word in kiwi.analyze(text)[0][0] if word.tag in {'NNG', 'NNP', 'NNB', 'NR', 'NP'}]
    normalized_words = []
    for word in words:
        word = remove_particles(word, particles)
        if word not in custom_stopwords and len(word) > 1:
            normalized_words.append(word)
    return normalized_words

def remove_particles(word, particles):
    for particle in particles:
        if word.endswith(particle):
            return word[:-len(particle)]
    return word

def create_word_cloud(df):
    text = ' '.join(df['description'].dropna().tolist())
    normalized_words = normalize_text(text)
    word_counts = Counter(normalized_words)
    
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=malgun_path).generate_from_frequencies(word_counts)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    wordcloud_image_path = os.path.join('static', 'uploads', 'wordcloud.png')
    plt.savefig(wordcloud_image_path)
    plt.close()
    return wordcloud_image_path

def create_pie_chart(df):
    category_counts = df['category1'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(category_counts, autopct='%1.1f%%', startangle=90, textprops=dict(color="w"))

    for i, text in enumerate(texts):
        size = category_counts[i]
        text.set_fontsize(10 + 20 * (size / max(category_counts)))

    for i, autotext in enumerate(autotexts):
        autotext.set_text(f'{category_counts.index[i]}: {autotext.get_text()}')

    plt.setp(autotexts, size=10, weight="bold")
    plt.title('News Category Distribution')
    plt.ylabel('')

    pie_chart_path = os.path.join('static', 'uploads', 'pie_chart.png')
    plt.tight_layout()
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path



def create_histogram(df):
    plt.figure(figsize=(10, 5))
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    df['pub_date'].hist(bins=20)
    plt.title('Publication Date Distribution')
    plt.xlabel('Publication Date')
    plt.ylabel('Frequency')
    histogram_path = os.path.join('static', 'uploads', 'histogram.png')
    plt.savefig(histogram_path)
    plt.close()
    return histogram_path

def create_stacked_bar_chart(df, time_period):
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    
    if time_period == 'date':
        time_series = df.groupby([df['pub_date'].dt.date, 'sentiment']).size().unstack().fillna(0)
    elif time_period == 'month':
        time_series = df.groupby([df['pub_date'].dt.to_period('M'), 'sentiment']).size().unstack().fillna(0)
    elif time_period == 'year':
        time_series = df.groupby([df['pub_date'].dt.year, 'sentiment']).size().unstack().fillna(0)
    else:
        raise ValueError("Invalid time period. Choose from 'date', 'month', or 'year'.")
    
    time_series = time_series.sort_index()  # Ensure the series is sorted by time
    
    # Plot the stacked bar chart
    time_series.plot(kind='bar', stacked=True, color=['red', 'yellow', 'green'], figsize=(10, 5))
    plt.title('News Sentiment Over Time')
    plt.xlabel(time_period.capitalize())
    plt.ylabel('Number of News Articles')
    stacked_bar_chart_path = os.path.join('static', 'uploads', 'stacked_bar_chart.png')
    plt.tight_layout()
    plt.savefig(stacked_bar_chart_path)
    plt.close()
    return stacked_bar_chart_path

def create_treemap_chart(df):
    company_mentions = df['description'].apply(lambda x: [word for word in normalize_text(x) if word in important_companies])
    company_counts = pd.Series([company for sublist in company_mentions for company in sublist]).value_counts()

    labels = company_counts.index
    sizes = company_counts.values

    fig, ax = plt.subplots(figsize=(12, 8))
    norm_sizes = [10 + 30 * (size / max(sizes)) for size in sizes]

    # Plot the treemap without duplicate labels
    squarify.plot(sizes=sizes, label=labels, alpha=.8, color=plt.cm.Paired(range(len(labels))))
    for i, rect in enumerate(squarify.squarify(sizes=sizes, x=0, y=0, dx=100, dy=100)):
        x = rect['x'] + (rect['dx'] / 2)
        y = rect['y'] + (rect['dy'] / 2)
        if labels[i] not in [t.get_text() for t in ax.texts]:
            ax.text(x, y, labels[i], ha='center', va='center', fontsize=norm_sizes[i])

    plt.axis('off')
    plt.title('Treemap of Important Companies Mentioned')

    treemap_chart_path = os.path.join('static', 'uploads', 'treemap_chart.png')
    plt.tight_layout()
    plt.savefig(treemap_chart_path)
    plt.close()
    return treemap_chart_path



def get_most_published_headline(df):
    # Group by title and get the count of each title
    title_counts = df['title'].value_counts()
    if not title_counts.empty:
        # Get the most frequent title
        most_published_headline = title_counts.idxmax()
    else:
        most_published_headline = "No headlines available"
    return most_published_headline

def create_network_graph(df, keyword):
    def extract_keywords(text):
        return normalize_text(text)

    # Avoid SettingWithCopyWarning by using .loc
    df.loc[:, 'title_keywords'] = df['title'].apply(extract_keywords)
    df.loc[:, 'description_keywords'] = df['description'].apply(extract_keywords)

    G = nx.Graph()
    keyword_related_nodes = Counter()

    for _, row in df.iterrows():
        title_keywords = row['title_keywords']
        if keyword in title_keywords:
            for other_keyword in title_keywords:
                if other_keyword != keyword:
                    G.add_edge(keyword, other_keyword)
                    keyword_related_nodes[other_keyword] += 1

    for main_keyword, count in keyword_related_nodes.items():
        for _, row in df.iterrows():
            if main_keyword in row['title_keywords']:
                for sub_keyword in row['title_keywords']:
                    if sub_keyword != main_keyword and sub_keyword != keyword:
                        G.add_edge(main_keyword, sub_keyword)

    top_mentioned_keywords = dict(keyword_related_nodes.most_common(10))
    node_sizes = []
    for node in G.nodes():
        if node in top_mentioned_keywords:
            node_sizes.append(300 + top_mentioned_keywords[node] * 100)
        else:
            node_sizes.append(100)

    cmap = plt.cm.plasma
    norm = plt.Normalize(vmin=0, vmax=max(node_sizes))
    node_colors = [cmap(norm(size)) for size in node_sizes]

    pos = nx.spring_layout(G, k=0.3)
    plt.figure(figsize=(18, 18))
    nx.draw(G, pos, with_labels=True, font_family=font_prop.get_name(), font_size=12, font_weight='bold',
            node_color=node_colors, node_size=node_sizes, edge_color='gray', alpha=0.6, cmap=cmap)

    plt.title(f'Network Graph for Keyword "{keyword}"', fontsize=20, fontproperties=font_prop)
    os.makedirs('static/uploads', exist_ok=True)
    graph_image_path = 'static/uploads/network_graph.png'
    plt.savefig(graph_image_path, dpi=300)
    plt.close()

    # Create thumbnail
    thumbnail_path = 'static/uploads/network_graph_thumbnail.png'
    img = Image.open(graph_image_path)
    img.thumbnail((400, 400))  # Adjust the size as needed
    img.save(thumbnail_path)

    return graph_image_path, thumbnail_path
