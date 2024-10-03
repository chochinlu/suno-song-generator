from dotenv import load_dotenv
import gradio as gr
from pytubefix import YouTube
from pytubefix.cli import on_progress
import whisper
import os
# from openai import OpenAI
from langfuse.openai import OpenAI
from langfuse.decorators import observe
import json
import requests
from prompts import LYRICS_ANALYSIS_PROMPT, TITLE_GENERATION_PROMPT, LYRICS_GENERATION_PROMPT

load_dotenv()
client = OpenAI()

@observe()
def get_lyrics(youtube_link):
    try:
        # Download YouTube audio
        yt = YouTube(youtube_link, on_progress_callback=on_progress)
        print(f"Processing YouTube link: {youtube_link}")
        audio = yt.streams.get_audio_only()
        audio.download(filename="temp", mp3=True)

        # Transcribe audio using Whisper
        model = whisper.load_model("turbo")
        result = model.transcribe("temp.mp3")
        
        # Save transcription result to file
        with open("lyrics.txt", "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # Read and return lyrics
        with open("lyrics.txt", "r", encoding="utf-8") as f:
            lyrics = f.read()
        
        # Delete temporary audio file
        os.remove("temp.mp3")
        
        return lyrics if lyrics else "No lyrics found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@observe()
def analyze_song(lyrics):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LYRICS_ANALYSIS_PROMPT},
            {"role": "user", "content": f"Analyze these lyrics:\n\n{lyrics}"}
        ],
        max_tokens=500
    )

    analysis = response.choices[0].message.content
    
    # Parse JSON response
    try:
        analysis_json = json.loads(analysis)
        song_style = analysis_json.get("songStyle", "Cannot analyze song style")
        instruments = analysis_json.get("instruments", "Cannot analyze instrument arrangement")
    except json.JSONDecodeError:
        # If JSON parsing fails, use simple text splitting
        parts = analysis.split("Song structure analysis:")
        song_style = parts[0].replace("Song style:", "").strip()
        instruments = parts[1].strip() if len(parts) > 1 else "Cannot analyze instrument arrangement"

    return song_style, instruments

@observe()
def generate_title(title, lyrics, style, language, thought):
    print(title, lyrics, style, language, thought)
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
def generate_song(generated_lyrics, style_input, title_input):
    url = f"{os.getenv('SUNO_API_HOST')}/api/custom_generate"
    payload = {
        "prompt": generated_lyrics,
        "title": title_input,
        "tags": style_input,
        "make_instrumental": False,
        "wait_audio": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        outputs = []
        for song in result[:2]:
            outputs.extend([song['image_url'], song['audio_url']])
        
        while len(outputs) < 4:
            outputs.extend([None, None])
        
        return *outputs, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    except requests.RequestException as e:
        error_message = f"Error generating song: {str(e)}"
        return None, None, None, None, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

@observe()
def update_style_input(song_style):
    return song_style

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

with gr.Blocks() as demo:
    youtube_link = gr.Text(label="Enter YouTube Song Link:")
    get_lyrics_btn = gr.Button("Get Lyrics")
    lyrics_output = gr.Textbox(label="Lyrics:", lines=10, interactive=True, placeholder="You can paste or edit lyrics here...")
    
    get_lyrics_btn.click(fn=get_lyrics, inputs=youtube_link, outputs=lyrics_output)
    
    analyze_btn = gr.Button("Analyze")
    with gr.Row():
        song_style = gr.Textbox(label="Song Style")
        instruments = gr.Textbox(label="Instruments and Vocal Arrangement")
    
    analyze_btn.click(fn=analyze_song, inputs=lyrics_output, outputs=[song_style, instruments])
    
    language_select = gr.Dropdown(choices=["Chinese", "English", "Japanese"], label="Select Language")
    
    with gr.Row():
        with gr.Column():
            your_thought_input = gr.Textbox(label="Enter your thought here:", lines=5, placeholder="You can paste or edit your thought about the song here...")

            title_input = gr.Textbox(label="Enter or edit song title here:", placeholder="You can paste or edit song title here...")
            generate_title_btn = gr.Button("Generate Song Title")
            
            generate_title_btn.click(
                fn=generate_title,
                inputs=[title_input, lyrics_output, song_style, language_select, your_thought_input],
                outputs=title_input
            )
            
            style_input = gr.Textbox(label="Enter or edit song style:", placeholder="You can generate or edit song style here...", interactive=True)
            generate_style_btn = gr.Button("Generate Song Style")
            
            generate_style_btn.click(
                fn=update_style_input,
                inputs=song_style,
                outputs=style_input
            )
            
        with gr.Column():
            lyrics_input = gr.Textbox(label="Enter or edit lyrics here:", lines=10, placeholder="You can paste or edit lyrics here...",interactive=True)
            generate_lyrics_btn = gr.Button("Generate Song Lyric")
            
            generate_lyrics_btn.click(
                fn=generate_lyrics,
                inputs=[instruments, language_select, your_thought_input],
                outputs=lyrics_input
            )
    
    generate_song_btn = gr.Button("Generate the Song at Suno")
    
    with gr.Row():
        with gr.Column():
            image_output1 = gr.Image(label="Song 1 Image", visible=False)
            audio_output1 = gr.Audio(label="Song 1 Audio", visible=False)
        
        with gr.Column():
            image_output2 = gr.Image(label="Song 2 Image", visible=False)
            audio_output2 = gr.Audio(label="Song 2 Audio", visible=False)

    generate_song_btn.click(
        fn=generate_song,
        inputs=[lyrics_input, style_input, title_input],
        outputs=[
            image_output1, audio_output1,
            image_output2, audio_output2,
            image_output1, audio_output1,
            image_output2, audio_output2
        ]
    )

demo.launch()