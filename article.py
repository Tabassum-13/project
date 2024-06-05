# import streamlit as st
# import aiohttp
# import asyncio
# from googlesearch import search
# import newspaper
# import pyttsx3
# from bs4 import BeautifulSoup
# import subprocess
# import nltk
# nltk.download('punkt')

# nltk.data.path.append('C:\Users\dell\Downloads\punkt.zip\punkt')

# engine = pyttsx3.init()

# st.title('Summarizer and Recommender')

# def is_url(input_text):
#     return input_text.startswith('http://') or input_text.startswith('https://')

# async def fetch_article_metadata(session, url):
#     try:
#         async with session.get(url) as response:
#             text = await response.text()
#             soup = BeautifulSoup(text, 'html.parser')
            
#             title = soup.find('title').get_text() if soup.find('title') else 'No title'
#             og_image = soup.find('meta', property='og:image')
#             image_url = og_image['content'] if og_image else None
            
#             return {
#                 'title': title,
#                 'top_image': image_url,
#                 'url': url
#             }
#     except Exception as e:
#         return None

# async def fetch_recommended_articles(query):
#     try:
#         urls = search(query, num_results=6)
#         async with aiohttp.ClientSession() as session:
#             tasks = [fetch_article_metadata(session, url) for url in urls]
#             articles = await asyncio.gather(*tasks)
#             return [article for article in articles if article]
#     except Exception as e:
#         st.error(f'Sorry, something went wrong: {e}')
#         return []

# url_or_text = st.text_input('', placeholder='Paste the URL of the article or enter a query and press Enter')

# if url_or_text:
#     if is_url(url_or_text):
#         try:
#             article = newspaper.Article(url_or_text)
#             article.download()
#             article.parse()

#             img = article.top_image
#             st.image(img)

#             title = article.title
#             st.subheader(title)

#             authors = article.authors
#             st.text(','.join(authors))

#             article.nlp()

#             keywords = article.keywords
#             st.subheader('Keywords:')
#             st.write(', '.join(keywords))

#             tab1, tab2 = st.tabs(["Full Text", "Summary"])
#             with tab1:
#                 st.subheader('Full Text')
#                 txt = article.text.replace('Advertisement', '')
#                 st.write(txt)
#             with tab2:
#                 st.subheader('Summary')
#                 summary = article.summary.replace('Advertisement', '')
#                 st.write(summary)

#             if st.button("Read Summary"):
#                 engine.say(summary)
#                 engine.runAndWait()

#         except Exception as e:
#             st.error(f'Sorry, something went wrong: {e}')

#     else:
#         st.subheader('Recommended Articles')
#         try:
#             articles = asyncio.run(fetch_recommended_articles(url_or_text))
#             for article in articles:
#                 col1, col2 = st.columns([2, 1])

#                 with col1:
#                     st.markdown(f"**[{article['title']}]({article['url']})**")
#                 with col2:
#                     if article['top_image']:
#                         st.image(article['top_image'], width=150, use_column_width=True)
#         except Exception as e:
#             st.error(f'Sorry, something went wrong: {e}')





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

# Download nltk data
nltk.download('punkt')

# Append nltk data path
nltk_data_path = os.path.join('C:', 'Users', 'dell', 'Downloads', 'punkt.zip', 'punkt')
nltk.data.path.append(nltk_data_path)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Streamlit app title
st.title('Summarizer and Recommender')

def is_url(input_text):
    st.write("Checking if input is URL:", input_text)
    return input_text.startswith('http://') or input_text.startswith('https://')

async def fetch_article_metadata(session, url):
    st.write("Fetching article metadata for URL:", url)
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
        st.write(f"Error fetching metadata for {url}: {e}")
        return None

async def fetch_recommended_articles(query):
    st.write("Fetching recommended articles for query:", query)
    try:
        urls = search(query, num_results=6)
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_article_metadata(session, url) for url in urls]
            articles = await asyncio.gather(*tasks)
            st.write("Fetched articles:", articles)
            return [article for article in articles if article]
    except Exception as e:
        st.error(f'Sorry, something went wrong: {e}')
        return []

url_or_text = st.text_input('', placeholder='Paste the URL of the article or enter a query and press Enter')

if url_or_text:
    st.write("Input received:", url_or_text)
    if is_url(url_or_text):
        st.write("Input is a URL")
        try:
            article = newspaper.Article(url_or_text)
            article.download()
            article.parse()
            st.write("Article downloaded and parsed")

            img = article.top_image
            if img:
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
        st.write("Input is a query")
        st.subheader('Recommended Articles')
        try:
            articles = asyncio.run(fetch_recommended_articles(url_or_text))
            for article in articles:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**[{article['title']}]({article['url']})**")
                with col2:
                    if article['top_image']:
                        st.image(article['top_image'], width=150, use_column_width=True)
        except Exception as e:
            st.error(f'Sorry, something went wrong: {e}')
