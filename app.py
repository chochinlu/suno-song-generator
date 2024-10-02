import gradio as gr
from pytube import YouTube
import whisper
import os

def get_lyrics(youtube_link):
    try:
        # Download YouTube audio
        yt = YouTube(youtube_link)
        audio = yt.streams.filter(only_audio=True).first()
        audio.download(filename="temp.mp3")

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

def analyze_song(lyrics):
    # Implement song analysis logic here
    # Currently returns placeholder text
    song_style = "Song style analysis will be displayed here"
    instruments = "Instruments and vocal arrangement analysis will be displayed here"
    return song_style, instruments

def generate_song_component(component_type, input_text):
    # Implement song component generation logic here
    # Currently returns input text
    return f"Generated {component_type}: {input_text}"

def generate_song():
    # Implement full song generation logic here
    # Currently returns placeholder text
    return "Processing... / Your song is ready: [Link to generated song]"

with gr.Blocks() as demo:
    youtube_link = gr.Textbox(label="Enter YouTube Song Link")
    get_lyrics_btn = gr.Button("Get Lyrics")
    lyrics_output = gr.Textbox(label="Lyrics will be displayed here...")
    
    analyze_btn = gr.Button("Analysis")
    with gr.Row():
        song_style = gr.Textbox(label="Song Style")
        instruments = gr.Textbox(label="Instruments and Vocal Arrangement")
    
    language_select = gr.Dropdown(choices=["Chinese", "English", "Japanese"], label="Select Language")
    
    with gr.Row():
        with gr.Column():
            title_input = gr.Textbox(label="Enter or edit song title here...")
            generate_title_btn = gr.Button("Generate Song Title")
        with gr.Column():
            lyrics_input = gr.Textbox(label="Enter or edit lyrics here...", lines=5)
            generate_lyrics_btn = gr.Button("Generate Song Lyric")
    
    style_input = gr.Textbox(label="Enter or edit song style here...")
    generate_style_btn = gr.Button("Generate Song Style")
    
    generate_song_btn = gr.Button("Generate the Song at Suno")
    song_output = gr.Textbox(label="Processing... / Your song is ready: [Link to generated song]")

    get_lyrics_btn.click(get_lyrics, inputs=youtube_link, outputs=lyrics_output)
    analyze_btn.click(analyze_song, inputs=lyrics_output, outputs=[song_style, instruments])
    generate_title_btn.click(generate_song_component, inputs=[gr.Textbox(value="title"), title_input], outputs=title_input)
    generate_lyrics_btn.click(generate_song_component, inputs=[gr.Textbox(value="lyrics"), lyrics_input], outputs=lyrics_input)
    generate_style_btn.click(generate_song_component, inputs=[gr.Textbox(value="style"), style_input], outputs=style_input)
    generate_song_btn.click(generate_song, outputs=song_output)

demo.launch()