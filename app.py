import gradio as gr
from pytubefix import YouTube
from pytubefix.cli import on_progress
import whisper
import os
from openai import OpenAI
import json

client = OpenAI()

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

def analyze_song(lyrics):
    system_prompt = """
    You are a lyrics analysis expert. After analyzing the lyrics, provide:
    - Song style: Use fewer than 100 characters to analyze the possible style of the song, using brief words as separators.
    - Song structure analysis: Analyze the composition of the song's sections, including possible vocal styles and the combination of one to three instruments.

    Example output:
    - Song style: Rock/Pop; Empowering; Emotional; Introspective; Dynamic

    - Song structure analysis: 
      - Intro: Instrumental buildup, setting an emotional tone, possibly with guitar and keyboard.
      - Verse: Reflective vocal style, emphasizing struggle and determination, accompanied by guitar and light percussion.
      - Chorus: Powerful delivery, showcasing strong vocals, energetic instrumentation with drums and electric guitar, uplifting message.
      - Bridge: Shift to a softer, contemplative vocal style, using strings or piano to enhance emotion.
      - Outro: Repetition of key themes from the chorus, leading to a climactic finish with full instrumental support.

    Please provide the analysis in the following JSON format:
    {
        "songStyle": "Brief description of song style",
        "instruments": "Detailed analysis of song structure and instruments"
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
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

def generate_title(title, lyrics, style, language):
    prompt = f"""
    Based on the following information, generate a catchy and appropriate song title:
    
    Current title (if any): {title}
    Lyrics excerpt: {lyrics[:200]}...
    Song style: {style}
    Language: {language}
    
    Please provide only the generated title in the specified language, without any additional explanation.
    If the language is Chinese, use Traditional Chinese characters.
    Do not include any quotation marks or parentheses at the beginning or end of the title.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative songwriter specializing in crafting catchy song titles in multiple languages."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=30
    )
    
    generated_title = response.choices[0].message.content.strip()
    # Remove possible quotation marks and parentheses at the beginning or end of the title
    generated_title = generated_title.strip('"\'()[]{}')
    
    return generated_title

def generate_song_component(component_type, input_text):
    # Implement song component generation logic here
    # Currently returns input text
    return f"Generated {component_type}: {input_text}"

def generate_song():
    # Implement full song generation logic here
    # Currently returns placeholder text
    return "Processing... / Your song is ready: [Link to generated song]"

def update_style_input(song_style):
    return song_style

def generate_lyrics(instruments, language, thought):
    prompt = f"""
    Based on the following information, generate song lyrics:
    
    Instruments and arrangement: {instruments}
    Language: {language}
    Songwriter's thought: {thought}
    
    Please provide only the generated lyrics in the specified language, without any additional explanation.
    If the language is Chinese, use Traditional Chinese characters.
    """
    
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
            title_input = gr.Textbox(label="Enter or edit song title here:", placeholder="You can paste or edit song title here...")
            generate_title_btn = gr.Button("Generate Song Title")
            
            generate_title_btn.click(
                fn=generate_title,
                inputs=[title_input, lyrics_output, song_style, language_select],
                outputs=title_input
            )
            
            style_input = gr.Textbox(label="Enter or edit song style here:", placeholder="You can generate or edit song style here...")
            generate_style_btn = gr.Button("Generate Song Style")
            
            generate_style_btn.click(
                fn=update_style_input,
                inputs=song_style,
                outputs=style_input
            )
            
            your_thought_input = gr.Textbox(label="Enter your thought here:", lines=5, placeholder="You can paste or edit your thought about the song here...")
        with gr.Column():
            lyrics_input = gr.Textbox(label="Enter or edit lyrics here:", lines=18, placeholder="You can paste or edit lyrics here...")
            generate_lyrics_btn = gr.Button("Generate Song Lyric")
            
            generate_lyrics_btn.click(
                fn=generate_lyrics,
                inputs=[instruments, language_select, your_thought_input],
                outputs=lyrics_input
            )
    
    generate_song_btn = gr.Button("Generate the Song at Suno")
    song_output = gr.Markdown("Processing... / Your song is ready: [Link to generated song]")

demo.launch()