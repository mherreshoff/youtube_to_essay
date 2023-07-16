# YouTube To Essay

## What it Does
`youtube_to_essay` is a script which can, given a YouTube URL (or YouTube video id) produces a text file containg a nicely formatted transcript divided into paragraphs.  This can be useful if you want to skim a video to see if it's worth watching, or if you prefer consuming text to consuming video.

Generally speaking, it works best on lecture-style videos where almost all the speech is from a single person (the original YouTube transcript it cleans up doesn't have a concept of which speaker is which.)

## How it Works
`youtube_to_essay` starts by reading the page to get some metadata (title and author).  It then pulls the raw transcript from youtube using the [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/) library.  Then it splits the transcript into overlapping sections (of about 300 words each) and sends then in parallel to GPT4, requesting that it add punctuation and paragraph breaks.  Finally, it stiches the results together to produce the finished transcript.

## Setup Instructions
Before trying to set up `youtube_to_essay`, make sure you have OpenAI API access including the GPT4 API, since you will need it to run the script (you can try using GPT3.5 by setting the `MODEL` variable to `gpt-3.5-turbo`, but GPT3.5 will sometimes reword things which confuses the merge algorithm).  Once you have access, put your API key in the `OPENAI_API_KEY` environment variable so the script can see it.

With that out of the way, install python 3 if you don't already have it.  See [this page](https://realpython.com/installing-python/) if you need instructions.

Then you call install the libraries dependencies the script depends on by running the terminal command `pip3 install beautifulsoup4 click openai requests youtube-transcript-api`.

# Running
To run the script just run `python3 youtube_to_essay.py $VIDEO $OUTPUT_FILE` where `$VIDEO` is the URL or just the YouTube Video ID (the sequence of letters after `?v=` in the YouTube video URL) you want an essay style transcript for, and `$OUTPUT_FILE` is the name of the file the script will put the essay in.

A typical run on a ten minute video takes about 25 seconds (largely waiting for
Open AI's servers to get back to us).  API costs should be about 20 cents per thousand
words.