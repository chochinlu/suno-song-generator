from dotenv import load_dotenv
import gradio as gr
from ai_generation_functions import (
    get_lyrics, analyze_song, generate_title, 
    generate_song, update_style_input, generate_lyrics
)

def update_analyze_btn(lyrics):
    return gr.update(interactive=bool(lyrics.strip()))

with gr.Blocks() as demo:
    youtube_link = gr.Text(label="Enter YouTube Song Link:")
    get_lyrics_btn = gr.Button("Get Lyrics")
    lyrics_output = gr.Textbox(label="Lyrics:", lines=10, interactive=True, placeholder="You can paste or edit lyrics here...")
    
    get_lyrics_btn.click(fn=get_lyrics, inputs=youtube_link, outputs=lyrics_output)
    
    analyze_btn = gr.Button("Analyze Song", interactive=False)
    lyrics_output.change(fn=update_analyze_btn, inputs=lyrics_output, outputs=analyze_btn)
    
    with gr.Column():
        song_style = gr.Textbox(label="Song Style", interactive=False)
        instruments = gr.Textbox(label="Instruments and Vocal Arrangement", interactive=False)

    analyze_btn.click(fn=analyze_song, inputs=lyrics_output, outputs=[song_style, instruments])
    
    language_select = gr.Dropdown(
        choices=[
            "Chinese",
            "English",
            "Japanese",
            "Spanish",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Russian",
            "Korean",
            "Arabic",
            "Hindi",
            "Dutch"
        ],
        label="Select Language"
    )
    
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
    
    with gr.Row() as output_row:
        with gr.Column():
            image_output1 = gr.Image(label="Song 1 Image", visible=False)
            audio_output1 = gr.Audio(label="Song 1 Audio", visible=False)
        
        with gr.Column():
            image_output2 = gr.Image(label="Song 2 Image", visible=False)
            audio_output2 = gr.Audio(label="Song 2 Audio", visible=False)

    processing_msg = gr.Markdown(visible=False)
    
    def show_processing_msg():
        return gr.update(visible=True, value="Processing...")

    def hide_processing_msg():
        return gr.update(visible=False)

    generate_song_btn.click(
        fn=show_processing_msg,
        outputs=processing_msg
    ).then(
        fn=generate_song,
        inputs=[lyrics_input, style_input, title_input],
        outputs=[
            image_output1, audio_output1,
            image_output2, audio_output2,
            image_output1, audio_output1,
            image_output2, audio_output2,
            processing_msg
        ]
    )

    suno_link = gr.HTML('''
    <p style="text-align: center; font-size: 28px; margin-top: 20px;">
        <a href="https://www.suno.com" target="_blank" style="color: #4a90e2; text-decoration: none; font-weight: bold;">
            Visit Suno Website
        </a>
    </p>
''')

demo.launch()