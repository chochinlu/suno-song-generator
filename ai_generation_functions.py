from dotenv import load_dotenv
from langfuse.decorators import observe
from pytubefix import YouTube, extract
from pytubefix.cli import on_progress

from youtube_transcript_api import YouTubeTranscriptApi
import whisper
import os
import json
from langfuse.openai import OpenAI
import requests
from requests.exceptions import Timeout, RequestException
import gradio as gr
from prompts import TITLE_GENERATION_PROMPT, LYRICS_GENERATION_PROMPT, SONG_STYLE_GENERATION_PROMPT, LYRICS_ANALYSIS_SONG_STYLE_PROMPT, LYRICS_ANALYSIS_INSTRUMENTS_PROMPT, music_categories
import tempfile
import PyPDF2

load_dotenv()
client = OpenAI()


@observe()
def get_lyrics(youtube_link):
    try:
        # Download YouTube audio
        yt = YouTube(youtube_link, on_progress_callback=on_progress)
        audio_stream = yt.streams.filter(only_audio=True).first()
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_stream.download(
            output_path=os.path.dirname(temp_audio_file.name),
            filename=os.path.basename(temp_audio_file.name)
        )

        # Transcribe audio using Whisper
        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_file.name)

        # Get the transcription text directly from the result
        lyrics = result["text"]

        # Clean up the temporary audio file
        temp_audio_file.close()
        os.remove(temp_audio_file.name)

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
    print(f"Language selected: {language}")
    prompt = f"""
Based on the following lyrics and style, generate a song title in {language}.

Lyrics:
{lyrics}

Style:
{style}

Your Thought:
{thought}
"""
    system_prompt = f"You are a creative songwriter specializing in crafting catchy song titles. Generate the song title in {language}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
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
def generate_song(generated_lyrics, style_input, title_input):
    url = f"{os.getenv('SUNO_API_HOST')}/api/custom_generate"
    payload = {
        "prompt": generated_lyrics,
        "title": title_input,
        "tags": style_input,
        "make_instrumental": False,
        "wait_audio": True
    }
    
    timeout = 600  # 10 minutes

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        
        outputs = []
        for song in result[:2]:
            outputs.extend([song['image_url'], song['audio_url']])
        
        while len(outputs) < 4:
            outputs.extend([None, None])
        
        return *outputs, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)
    except Timeout:
        error_message = f"Request timed out after {timeout} seconds. Please try again later."
    except RequestException as e:
        error_message = f"Error generating song: {str(e)}"
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
    
    return None, None, None, None, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True, value=error_message)

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
def generate_lyrics(instruments, language, thought, uploaded_file):
    # Read the content of the uploaded file
    file_content = read_uploaded_file(uploaded_file)
    
    # Update the prompt to include the file content
    prompt = LYRICS_GENERATION_PROMPT.format(
        instruments=instruments,
        language=language,
        thought=thought,
        file_content=file_content
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

def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        if uploaded_file.name.endswith('.txt'):
            with open(uploaded_file.name, 'r', encoding='utf-8') as f:
                content = f.read()
        elif uploaded_file.name.endswith('.pdf'):
            content = extract_text_from_pdf(uploaded_file)
        else:
            content = ""
        return content
    except Exception as e:
        print(f"Error reading uploaded file: {e}")
        return ""

def extract_text_from_pdf(uploaded_file):
    content = ""
    try:
        with open(uploaded_file.name, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                content += page.extract_text()
        return content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""