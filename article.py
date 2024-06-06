import streamlit as st
import aiohttp
import asyncio
from googlesearch import search
import newspaper
import pyttsx3
from bs4 import BeautifulSoup
import subprocess
import nltk
import os

def download_nltk_data():
    nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    nltk.data.path.append(nltk_data_dir)
    
    # Check if 'punkt' is already downloaded
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True, download_dir=nltk_data_dir)

# Ensure the necessary NLTK data package is downloaded
download_nltk_data()

engine = pyttsx3.init()

st.title('Article Summarizer and Recommender')

def is_url(input_text):
    return input_text.startswith('http://') or input_text.startswith('https://')

async def fetch_article_metadata(session, url):
    try:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            
            title = soup.find('title').get_text() if soup.find('title') else 'No title'
            og_image = soup.find('meta', property='og:image')
            image_url = og_image['content'] if og_image else None
            
            return {
                'title': title,
                'top_image': image_url,
                'url': url
            }
    except Exception as e:
        return None

async def fetch_recommended_articles(query):
    try:
        urls = search(query, num_results=6)
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_article_metadata(session, url) for url in urls]
            articles = await asyncio.gather(*tasks)
            return [article for article in articles if article]
    except Exception as e:
        st.error(f'Sorry, something went wrong: {e}')
        return []

url_or_text = st.text_input('', placeholder='Paste the URL of the article or enter a query and press Enter')


st.markdown("With this app you can make the summary of the article. All you have to do is to keep the link of the article or you can aslo search titles of the articles to get the suggestions Once you click enter you can see the results:")
st.markdown("1. the summary of the Article,") 
st.markdown("2. suggestions or recommendations of articles with their urls,") 


if url_or_text:
    if is_url(url_or_text):
        try:
            article = newspaper.Article(url_or_text)
            article.download()
            article.parse()

            img = article.top_image
            st.image(img)

            title = article.title
            st.subheader(title)

            authors = article.authors
            st.text(','.join(authors))

            article.nlp()

            keywords = article.keywords
            st.subheader('Keywords:')
            st.write(', '.join(keywords))

            tab1, tab2 = st.tabs(["Full Text", "Summary"])
            with tab1:
                st.subheader('Full Text')
                txt = article.text.replace('Advertisement', '')
                st.write(txt)
            with tab2:
                st.subheader('Summary')
                summary = article.summary.replace('Advertisement', '')
                st.write(summary)

            if st.button("Read Summary"):
                engine.say(summary)
                engine.runAndWait()

        except Exception as e:
            st.error(f'Sorry, something went wrong: {e}')

    else:
        st.subheader('Recommended Articles')
        try:
            articles = asyncio.run(fetch_recommended_articles(url_or_text))
            for article in articles:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"[{article['title']}]({article['url']})")
                with col2:
                    if article['top_image']:
                        st.image(article['top_image'], width=150, use_column_width=True)
        except Exception as e:
            st.error(f'Sorry, something went wrong: {e}')
