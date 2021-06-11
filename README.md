## Youtube Video Comments Highlight Tool

### Problem
Want to be able to generate a highlight video from youtube videos. Manually clipping these time stamps are super time costly and tiring.

### Solution
Get comments from youtube video that follow a specific time stamp format. Clip these time stamps and stitch them together to output a highlight video.

### Set Up
1. run `pip install -r requirements.txt`
2. run `python main.py`
3. prompted to authenticate on gmail
4. copy paste token to terminal
5. download ffmpeg and add to environment variable (required by the library that is used to download YT video)

### How to use
1. enter links, press enter after each link
2. press f to start generating highlights