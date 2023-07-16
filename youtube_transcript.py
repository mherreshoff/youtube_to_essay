import difflib
import re
import os
import time

import bs4
import click
import multiprocessing
import openai
import openai.error
import requests
import youtube_transcript_api

SECTOR_LENGTH = 330
OVERLAP_LENGTH = 30

MODEL = "gpt-4"
    # Note: 3.5 was hallucinating extra sentences.
SYSTEM_PROMPT = """Clean up the transcript the user gives you, fixing spelling errors and adding punctuation as needed.
However, do not reword any sentences.
Include plenty of paragraph breaks.""".replace("\n", " ")

def init_openai(key=None):
    if key is None:
        key = os.environ.get("OPEN_AI_API_KEY")
    if key is None:
        raise ValueError("OPEN_AI_API_KEY environment variable is not set")
    openai.api_key = key

def ask_gpt(model: str, system_prompt: str, user_prompt: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages)
            print(response)
            return response.choices[0]["message"]["content"]
        except openai.error.RateLimitError:
            print("Rate limit error, waiting 30 seconds")
            time.sleep(30)


def clean_transcript_sector(transcript: str) -> str:
    return ask_gpt(MODEL, SYSTEM_PROMPT, transcript)

def merge_similar_strings(s1: str, s1_cutpoint: int, s2: str) -> str:
    # To find the best spot in `s2` for the transition point, we compute the
    # minimal list of edits to change s1 into s2, and then we walk through edits
    # to see where the character at `s1_cutpoint` in `s1` would end up in `s2`.
    print(f"Merging {s1[:s1_cutpoint]}|{s1[s1_cutpoint:]} ++++ {s2}")
    matcher = difflib.SequenceMatcher(None, s1, s2)

    s2_cutpoint = None
    previous_block_end = 0
    for (i, j, n) in matcher.get_matching_blocks():
        if previous_block_end <= s1_cutpoint < i:
            s2_cutpoint = j + (s1_cutpoint - i)
            break
        if i <= s1_cutpoint < i + n:
            s2_cutpoint = j + (s1_cutpoint - i)
            break

    print(f'Merged: {s1[:s1_cutpoint]}|{s2[s2_cutpoint:]}')
    return s1[:s1_cutpoint] + s2[s2_cutpoint:]

def merge_sectors(sector1, sector2, overlap_chars):
    s1 = sector1[-overlap_chars:]
    s2 = sector2[:overlap_chars]
    merged_portion = merge_similar_strings(s1, overlap_chars // 2, s2)

    return sector1[:-overlap_chars] + merged_portion + sector2[overlap_chars:]

def clean_transcript(transcript: str) -> str:
    transcript_words = re.split(r'\s+', transcript)
    # First we split the transcript into overlapping sectors:
    sectors = []
    sector_starts = []
    for i in range(0, len(transcript_words), SECTOR_LENGTH - OVERLAP_LENGTH):
        sector_starts.append(i)
        sectors.append(' '.join(transcript_words[i:i+SECTOR_LENGTH]))

    #for i in range(len(sectors)):
    #    with open('sector_%03d.txt' % i, 'w') as f:
    #        f.write(sectors[i])

    # Next we call the cleanup_transcript_sector function on each sector in parallel:
    with multiprocessing.Pool() as pool:
        cleaned_sectors = pool.map(clean_transcript_sector, sectors)

    #for i in range(len(cleaned_sectors)):
    #    with open('sector_%03d_cleaned.txt' % i, 'w') as f:
    #        f.write(cleaned_sectors[i])

    # Hack for testing:
    #cleaned_sectors = []
    #for i in range(12):
    #    with open('cleaned_sector_%03d.txt' % i, 'r') as f:
    #        cleaned_sectors.append(f.read())

    # Finally we merge the sectors back together:
    cleaned_transcript = cleaned_sectors[0]
    for i in range(1, len(cleaned_sectors)):
        overlap_chars = len(' '.join(transcript_words[sector_starts[i]:sector_starts[i] + OVERLAP_LENGTH]))
        cleaned_transcript = merge_sectors(cleaned_transcript, cleaned_sectors[i], overlap_chars)

    if not cleaned_transcript.endswith('\n'):
        cleaned_transcript += '\n'
    return cleaned_transcript

@click.command()
@click.argument('video')
@click.argument('output_file')
def main(video, output_file):
    m = re.search(r'v=([a-zA-Z0-9_-]+)', video)
    if m:
        video_id = m.group(1)
    else:
        video_id = video

    # First let's extract get the title and author from the video page:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    page_text = requests.get(video_url).text
    soup = bs4.BeautifulSoup(page_text, 'html.parser')
    title_tag = soup.find('title')
    title = None
    if title_tag:
        title = title_tag.text
        title = title.replace(" - YouTube", "")
    print(f"Got title: {title}")

    author = None
    author_tag = soup.find('link', {'itemprop': 'name'})
    if author_tag:
        author = author_tag.attrs.get('content', '')
    print(f"Got author: {author}")

    transcript = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
    original_text = ' '.join(word for line in transcript for word in line['text'].split())

    with open('original.txt', 'w') as f:
        f.write(original_text)

    cleaned_text = clean_transcript(original_text)

    with open(output_file, 'w') as f:
        if title:
            f.write("Video Title: " + title + "\n")
        if author:
            f.write("Video Author: " + author + "\n")
        f.write("\n")
        f.write(cleaned_text)



if __name__ == "__main__":
    main()