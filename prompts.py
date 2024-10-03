LYRICS_ANALYSIS_PROMPT = """
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
{{
    "songStyle": "Brief description of song style",
    "instruments": "Detailed analysis of song structure and instruments"
}}
"""

TITLE_GENERATION_PROMPT = """
Based on the following information, generate a catchy and appropriate title for a song:

Original title: {title}
Lyrics: {lyrics}[:200]...
Style: {style}
Language: {language}
Songwriter's thought: {thought}

Please provide only the generated title in the specified language, without any additional explanation.
If the language is Chinese, use Traditional Chinese characters.
Do not include any quotation marks or parentheses at the beginning or end of the title.
The generated title must clearly reflect the songwriter's thought, ensuring a strong connection between the two.
"""


LYRICS_GENERATION_PROMPT = """
Based on the following information, generate song lyrics:

Instruments and arrangement: {instruments}
Language: {language}
Songwriter's thought: {thought}

Requirements:
1. The lyrics should rhyme as much as possible, focusing on creating a melodic and rhythmic flow.
2. Ensure the rhyme scheme is appropriate for the song style and language.
3. Use internal rhymes and assonance to enhance the lyrical quality when applicable.

Please provide only the generated lyrics in the specified language, without any additional explanation.
If the language is Chinese, use Traditional Chinese characters.
"""
