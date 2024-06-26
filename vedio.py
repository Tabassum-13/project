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

st.title("Video Summarizer")
st.markdown("With this app you can summarize a Youtube vedio. All you have to do is to pass the link of the video and get the summary of the video:")
st.markdown("1. a summary of the video,") 
st.markdown("2. the topics that are discussed in the video,") 
st.markdown("3. Make sure that the video has transcript in english.")
st.markdown("Make sure your links are in the format: https://www.youtube.com/watch?v=HfNnuQOHAaw and not https://youtu.be/HfNnuQOHAaw")

st.title("Coming soon..!")
