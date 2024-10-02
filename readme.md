# Suno Song Generator

This Suno Song Generator is designed for users who are not necessarily music professionals (like myself). 

Have you ever listened to a song and thought, "Wow, this song is amazing! I wish I could create something like this," but you lack the knowledge of music production, genres, or instrumental details?

This tool allows you to:
1. Provide a YouTube link of a song you like or input related lyrics
2. Utilize AI analysis to generate a similar style and lyrics to the song you love
3. Customize the output to your preferences
4. Finally, use the Suno API to produce a song

With this generator, you can turn your musical inspiration into reality, even without extensive musical expertise.


## How to run

First, you need a Suno account. Register at [Suno](https://suno.ai/).


Create virtual environment (recommend) and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You need to start the Suno API server, please refer to the [Suno API](https://github.com/suno-ai/suno-public/tree/main/docs/api)

Start the Song Generator:

```bash
python app.py
```

The web app will run on http://localhost:7860
