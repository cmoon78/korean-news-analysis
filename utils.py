import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import os
import io
import base64
from collections import Counter
from kiwipiepy import Kiwi
from matplotlib.font_manager import FontProperties
import difflib
from textblob import TextBlob  # Add this line for sentiment analysis

# Set the path to Malgun Gothic font
malgun_path = 'C:/Windows/Fonts/malgun.ttf'  # Ensure this path is correct on your system

# Set the font properties for matplotlib
font_prop = FontProperties(fname=malgun_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # Ensure that minus signs are rendered correctly

# Load custom stop words from a file
custom_stopwords_path = 'custom_stopwords.txt'
with open(custom_stopwords_path, 'r', encoding='utf-8') as f:
    custom_stopwords = set(f.read().splitlines())

# Load company dictionary
company_info_path = 'KOSPI200_Industry_Info.xlsx'  # Ensure this path is correct on your system
company_df = pd.read_excel(company_info_path)

# Create a set of important companies
important_companies = set(company_df['Company_name'].dropna().tolist() + company_df['Company_name2'].dropna().tolist())

kiwi = Kiwi()

# Define particles to be removed
particles = set(['은', '는', '이', '가', '를', '도', '랑', '을'])

def remove_particles(word):
    for particle in particles:
        if word.endswith(particle):
            return word[:-len(particle)]
    return word

def normalize_text(text):
    words = [word.form for word in kiwi.analyze(text)[0][0] if word.tag in {'NNG', 'NNP', 'NNB', 'NR', 'NP'}]
    normalized_words = []
    for word in words:
        if word in important_companies:
            normalized_words.append(word)
        else:
            word = remove_particles(word)
            if word not in custom_stopwords and len(word) > 1:
                normalized_words.append(word)
    return normalized_words

def validate_csv(df):
    required_columns = {'item_id', 'title', 'description', 'pub_date', 'author', 'link', 'category1', 'category2', 'source_name'}
    if not required_columns.issubset(df.columns):
        missing_columns = required_columns - set(df.columns)
        raise ValueError(f"CSV file is missing columns: {missing_columns}")

def create_news_volume_graph(df, time_filter):
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    news_volume = df['pub_date'].dt.to_period(time_filter).value_counts().sort_index()
    
    plt.figure(figsize=(10, 5))
    news_volume.plot(kind='bar', color=['grey' if x != news_volume.idxmax() else 'red' for x in news_volume.index])
    plt.title('News Volume Over Time')
    plt.xlabel('Date')
    plt.ylabel('News Volume')
    plt.tight_layout()
    os.makedirs('static', exist_ok=True)
    plt.savefig('static/news_volume.png')
    plt.close()

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=malgun_path, stopwords=custom_stopwords).generate(text)
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img, format='png')
    img.seek(0)
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

def create_word_cloud(df):
    text = ' '.join(df['description'].dropna().tolist())
    normalized_text = ' '.join(normalize_text(text))
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=malgun_path, stopwords=custom_stopwords).generate(normalized_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    os.makedirs('static', exist_ok=True)
    plt.savefig('static/word_cloud.png')
    plt.close()

def create_network_graph(df, keyword):
    def extract_keywords(text):
        return normalize_text(text)

    df['title_keywords'] = df['title'].apply(extract_keywords)
    df['description_keywords'] = df['description'].apply(extract_keywords)

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
    os.makedirs('static', exist_ok=True)
    plt.savefig('static/network_graph.png', dpi=300)
    plt.close()

def create_keyword_summary(df):
    text = ' '.join(df['description'].dropna().tolist())
    words = normalize_text(text)
    counter = Counter(words)
    top_keywords = counter.most_common(10)

    summary = "Top 10 Keywords:\n" + "\n".join([f"{word}: {count}" for word, count in top_keywords])
    os.makedirs('static', exist_ok=True)
    with open('static/keyword_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)

def prepare_filtered_news_data(df):
    return df[['pub_date', 'title', 'description', 'link']].sort_values(by='pub_date').to_dict(orient='records')

def get_total_stories(df, filtered_df):
    return len(df), len(filtered_df)

def get_highest_volume_date(df):
    highest_volume_date = df['pub_date'].value_counts().idxmax()
    highest_volume_count = df['pub_date'].value_counts().max()
    return highest_volume_date, highest_volume_count

def get_most_published_headline(df):
    headlines = df['title'].tolist()
    clustered_headlines = difflib.get_close_matches(headlines[0], headlines, n=len(headlines), cutoff=0.6)
    most_published_headline = max(set(clustered_headlines), key=clustered_headlines.count)
    headline_count = clustered_headlines.count(most_published_headline)
    headline_link = df[df['title'] == most_published_headline]['link'].values[0]
    return most_published_headline, headline_count, headline_link

def sentiment_analysis(df):
    positive_count = 0
    negative_count = 0
    positive_example = None
    negative_example = None

    for index, row in df.iterrows():
        analysis = TextBlob(row['description'])
        if analysis.sentiment.polarity > 0:
            positive_count += 1
            if positive_example is None:
                positive_example = {'title': row['title'], 'link': row['link']}
        elif analysis.sentiment.polarity < 0:
            negative_count += 1
            if negative_example is None:
                negative_example = {'title': row['title'], 'link': row['link']}

    return positive_count, negative_count, positive_example, negative_example
