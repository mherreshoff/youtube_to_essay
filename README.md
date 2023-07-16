# YouTube To Essay

## What it Does
`youtube_to_essay` is a script which, given a YouTube URL (or YouTube video id) produces a text file containg a nicely formatted transcript divided into paragraphs.  This can be useful if you want to skim a video to see if it's worth watching, or if you prefer consuming text to consuming video.

Generally speaking, it works best on lecture-style videos where almost all the speech is from a single person (the original YouTube transcript it cleans up doesn't have a concept of which speaker is which.)

## How it Works
`youtube_to_essay` starts by reading the video page to get some metadata (title and author).  It then pulls the raw transcript from youtube using the [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/) library.  It splits the transcript into overlapping sections (of about 300 words each) and sends then in parallel to GPT4, requesting that it add punctuation and paragraph breaks.  Once it has the pieces, it stiches the results together to produce the finished transcript.

## Setup Instructions
Before trying to set up `youtube_to_essay`, make sure you have OpenAI API access including the GPT4 API, since you will need it to run the script.  Once you have access, put your API key in the `OPENAI_API_KEY` environment variable so the script can see it.

With that out of the way, install Python 3 if you don't already have it.  See [this page](https://realpython.com/installing-python/) if you need instructions.

Then you call install the Python libraries the script depends on by running the terminal command: `pip3 install beautifulsoup4 click openai requests youtube-transcript-api`.

# Running
To run the script just run `python3 youtube_to_essay.py $VIDEO $OUTPUT_FILE` where `$VIDEO` is the URL or just the YouTube Video ID (the sequence of letters after `?v=` in the YouTube video URL) you want an essay style transcript for, and `$OUTPUT_FILE` is the name of the file the script will put the essay in.

A typical run on a ten minute video takes about 25 seconds (largely waiting for Open AI's servers to get back to us).  If you leave `MODEL` set to `gpt-4` API costs should be about 20 cents per thousand words.

# Future Work
* We could decrease API costs by switching to `gpt-3.5-turbo`.  Unfortunately, it seems to reword things more aggressively, which occasionaly creates awkward seams when the sections of text were merged back together.  Perhaps additional prompt engineering can fix this.