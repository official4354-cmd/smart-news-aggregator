from flask import Flask, render_template, request
from transformers import pipeline
import requests

app = Flask(__name__)

# Initialize summarization model
summarizer = pipeline("summarization")

@app.route('/')
def index():
    query = request.args.get("query")
    country = request.args.get("country", "us")  # Default: US
    category = request.args.get("category", "")  # Default: All categories

    # Build API URL dynamically based on user selection
    if query:
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey=c2a6db689461466faa1d2dbbe669f625"
    else:
        if category:
            url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey=c2a6db689461466faa1d2dbbe669f625"
        else:
            url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey=c2a6db689461466faa1d2dbbe669f625"

    response = requests.get(url)
    data = response.json()

    if "articles" not in data:
        return "Error: Unable to fetch articles. Check your API key or internet connection."

    articles = data["articles"]

    # Category keywords for auto-tagging
    categories = {
        "technology": ["tech", "software", "AI", "computer", "robot", "app", "internet"],
        "sports": ["match", "cricket", "football", "sports", "game", "player"],
        "politics": ["election", "government", "minister", "policy", "vote", "law"]
    }

    for article in articles:
        desc = article.get("description", "")
        if desc:
            try:
                summary = summarizer(desc, max_length=40, min_length=15, do_sample=False)
                article["summary"] = summary[0]['summary_text']
            except Exception:
                article["summary"] = desc
        else:
            article["summary"] = "No summary available."

        # Auto categorize
        description = desc.lower()
        auto_category = "general"
        for key, words in categories.items():
            if any(word in description for word in words):
                auto_category = key
                break
        article["category"] = auto_category

    return render_template(
        'index.html',
        articles=articles,
        query=query,
        country=country,
        category=category
    )

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

