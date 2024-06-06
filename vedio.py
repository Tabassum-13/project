import os
import sys
import subprocess
import streamlit as st
import aiohttp
import asyncio
from googlesearch import search
import newspaper
import pyttsx3
from bs4 import BeautifulSoup
import nltk
from transformers import pipeline, __version__ as transformers_version
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the YouTube API key
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    st.error("API key is not set. Please check your .env file.")

def download_nltk_data():
    nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    nltk.data.path.append(nltk_data_dir)
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True, download_dir=nltk_data_dir)

def ensure_dependencies():
    global tf_installed, torch_installed
    tf_installed = False
    torch_installed = False
    
    try:
        import tensorflow as tf
        st.write(f"TensorFlow version: {tf.__version__}")
        tf_installed = True
    except ImportError:
        st.info("TensorFlow not installed.")
    
    try:
        import torch
        st.write(f"PyTorch version: {torch.__version__}")
        torch_installed = True
    except ImportError:
        st.info("PyTorch not installed.")

    if not tf_installed and not torch_installed:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.0.0+cpu", "-f", "https://download.pytorch.org/whl/torch_stable.html"])
            import torch
            st.write(f"PyTorch version after installation: {torch.__version__}")
            torch_installed = True
        except subprocess.CalledProcessError as e:
            st.error(f"Error installing PyTorch: {e}")
            return False
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            return False
    
    return tf_installed or torch_installed

dependencies_installed = ensure_dependencies()

# Initialize summarizer if dependencies are installed
if dependencies_installed:
    try:
        st.write(f"Transformers version: {transformers_version}")
        if torch_installed:
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="pt")
        elif tf_installed:
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="tf")
        st.write("Summarizer model loaded successfully.")
    except Exception as e:
        st.error(f"Error loading summarizer model: {str(e)}")
        summarizer = None
else:
    summarizer = None

download_nltk_data()

engine = pyttsx3.init()
st.title('Video Summarizer')

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
            return {'title': title, 'top_image': image_url, 'url': url}
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

def summarize_text(text, max_chunk=1000):
    summarized_text = []
    num_iters = int(len(text) / max_chunk) + 1
    for i in range(num_iters):
        start = i * max_chunk
        end = min((i + 1) * max_chunk, len(text))
        chunk = text[start:end]
        if chunk:
            out = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summarized_text.append(out[0]['summary_text'])
    return " ".join(summarized_text)

def get_transcript(video_id, language='en'):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript([language])
        return " ".join([item['text'] for item in transcript.fetch()])
    except NoTranscriptFound:
        return None
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except VideoUnavailable:
        st.error("The video is unavailable.")
    except Exception as e:
        st.error(f"An error occurred while fetching the transcript: {str(e)}")
    return None

def get_youtube_video_details(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            snippet = data["items"][0]["snippet"]
            title = snippet["title"]
            thumbnail_url = snippet["thumbnails"]["high"]["url"]
            return title, thumbnail_url
    return None, None

url_or_text = st.text_input('', placeholder='Paste the URL of the article or enter a query and press Enter')

if url_or_text:
    if is_url(url_or_text):
        if summarizer:
            if 'youtube.com/watch' in url_or_text or 'youtu.be/' in url_or_text:
                if 'youtube.com/watch' in url_or_text:
                    video_id = url_or_text.split('v=')[-1]
                elif 'youtu.be/' in url_or_text:
                    video_id = url_or_text.split('/')[-1]
                
                video_title, thumbnail_url = get_youtube_video_details(video_id, api_key)
                
                if video_title and thumbnail_url:
                    st.image(thumbnail_url)
                    st.subheader(video_title)
                
                transcript = get_transcript(video_id)
                if not transcript:
                    st.error("Could not retrieve a transcript for the video.")
                else:
                    tab1, tab2 = st.tabs(["Full Text", "Summary"])
                    with tab1:
                        st.subheader('Full Text:')
                        st.write(transcript)
                    
                    with tab2:
                        summarized_text = summarize_text(transcript)
                        st.subheader('Summary:')
                        st.write(summarized_text)
            else:
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
            st.error("Summarizer model is not loaded.")
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
