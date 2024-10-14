import os
import requests
from requests.exceptions import Timeout, RequestException
import gradio as gr
from dotenv import load_dotenv
from langfuse.decorators import observe

load_dotenv()

@observe()
def generate_song(generated_lyrics, style_input, title_input):
    url = f"{os.getenv('SUNO_API_HOST')}/api/custom_generate"
    payload = {
        "prompt": generated_lyrics,
        "title": title_input,
        "tags": style_input,
        "make_instrumental": False,
        # "wait_audio": True
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
