# YouTube To Essay

## What it Does
`youtube_to_essay` is a script which can, given a YouTube URL (or YouTube video id) produces a text file containg a nicely formatted transcript divided into paragraphs.

Generally speaking, it works best on lecture-style videos where almost all the speech is from a single person.

## How it Works
`youtube_to_essay` starts by pulling the raw transcript from youtube using the [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/) library.  Then it splits the transcript into overlapping sections (of about 300 words each) and sends then in parallel to GPT3.5, requesting that it add punctuation and paragraph breaks.  Finally, it stiches the results together to produce the finished transcript.

## Setup Instructions
Before trying to set up `youtube_to_essay`, make sure you have OpenAI API access, since you will need it to run the script.  Once you have access, put your API key in the `OPENAI_API_KEY` environment variable so the script can see it.

With that out of the way, install python 3 if you don't already have it.  See [this page](https://realpython.com/installing-python/) if you need instructions.

Then you call install the libraries dependencies the script depends on by running the terminal command `pip3 install beautifulsoup4 click openai requests youtube-transcript-api`.