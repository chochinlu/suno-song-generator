from dotenv import load_dotenv
from langfuse.decorators import observe
from pytubefix import YouTube
from pytubefix.cli import on_progress
import whisper
import os
import json
from langfuse.openai import OpenAI
import requests
from requests.exceptions import Timeout, RequestException
import gradio as gr
from prompts import TITLE_GENERATION_PROMPT, LYRICS_GENERATION_PROMPT, SONG_STYLE_GENERATION_PROMPT, LYRICS_ANALYSIS_SONG_STYLE_PROMPT, LYRICS_ANALYSIS_INSTRUMENTS_PROMPT, music_categories

load_dotenv()
client = OpenAI()

@observe()
def get_lyrics(youtube_link):
    try:
        with open('tests/ly_1.txt', 'r', encoding='utf-8') as f:
            lyrics = f.read()
        return lyrics if lyrics else "No lyrics found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@observe()
def analyze_song_style(lyrics):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LYRICS_ANALYSIS_SONG_STYLE_PROMPT},
            {"role": "user", "content": f"Analyze these lyrics:\n\n{lyrics}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

@observe()
def analyze_song_instruments(lyrics):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LYRICS_ANALYSIS_INSTRUMENTS_PROMPT},
            {"role": "user", "content": f"Analyze these lyrics:\n\n{lyrics}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


@observe()
def analyze_song(lyrics):
    song_style = analyze_song_style(lyrics)
    instruments = analyze_song_instruments(lyrics)
    return song_style, instruments

@observe()
def generate_title(title, lyrics, style, language, thought):
    prompt = TITLE_GENERATION_PROMPT.format(
        title=title,
        lyrics=lyrics,
        style=style,
        language=language,
        thought=thought
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative songwriter specializing in crafting catchy song titles in multiple languages."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.5
    )
    
    generated_title = response.choices[0].message.content.strip()
    # Remove possible quotation marks and parentheses at the beginning or end of the title
    generated_title = generated_title.strip('"\'()[]{}')
    
    return generated_title

@observe()
def update_style_input(song_style, thought=""):
    prompt = SONG_STYLE_GENERATION_PROMPT.format(
        style=song_style,
        thought=thought,
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative music style generator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=60,
        temperature=0.7
    )
    
    generated_style = response.choices[0].message.content.strip()
    return generated_style

@observe()
def generate_lyrics(instruments, language, thought):
    prompt = LYRICS_GENERATION_PROMPT.format(
        instruments=instruments,
        language=language,
        thought=thought
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a talented songwriter capable of creating lyrics in multiple languages."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    generated_lyrics = response.choices[0].message.content.strip()
    return generated_lyrics

