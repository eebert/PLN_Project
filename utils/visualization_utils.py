# notebooks-visualization_utils.py
import matplotlib.pyplot as plt
import seaborn as sns

def create_histogram(data, title, x_label, y_label, bins=30):
    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=bins, kde=True)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

def create_wordcloud(text, title, width=800, height=800, background_color='white', stopwords=None, min_font_size=10):
    from wordcloud import WordCloud
    wordcloud = WordCloud(width=width, height=height, background_color=background_color, stopwords=stopwords, min_font_size=min_font_size).generate(text)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()
    
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.title(title)
    plt.tight_layout(pad=0)
    plt.show()

def create_bar_chart(data, title, x_label, y_label):
    plt.figure(figsize=(12, 6))
    sns.barplot(x=list(data.keys()), y=list(data.values()))
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.show()

def create_countplot(data, x_var, title, order=None):
    plt.figure(figsize=(12, 6))
    sns.countplot(x=x_var, data=data, order=order)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()

def create_boxplot(data, x_var, y_var, title):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x=x_var, y=y_var, data=data)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()
