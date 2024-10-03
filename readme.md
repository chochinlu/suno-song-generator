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

Create `.env` file and add the following environment variables:

```bash
OPENAI_API_KEY=<your_openai_api_key>
```


You need to start the Suno API server, please refer to the [Suno API](https://github.com/gcui-art/suno-api)

Start the Song Generator:

```bash
python app.py
```

The web app will run on http://localhost:7860

## Langfuse

[Langfuse](https://www.langfuse.com/) is an open-source LLM engineering platform that helps teams collaboratively debug, analyze, and iterate on their LLM applications.

The app has added the langfuse observer decorator to the functions that interact with the OpenAI API.

You can use the self-hosted LangFuse to observe the tracing data. Flow [this repository](https://github.com/gcui-art/langfuse-langsmith-self-hosted) and run `docker compose up -d` to start the LangFuse server.

Fllow the instruction in the langfuse server, sign up for an account, create a new project, and get the `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`, add them to the `.env` file: 

```env
LANGFUSE_SECRET_KEY=<your_langfuse_secret_key>
LANGFUSE_PUBLIC_KEY=<your_langfuse_public_key>
LANGFUSE_HOST="http://localhost:3000"
```

Then, you can view the tracing data at http://localhost:3000/
