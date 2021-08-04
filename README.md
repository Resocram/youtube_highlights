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

### How to use - dev
1. enter links, press enter after each link
2. press f to start generating highlights
3. after the highlight video has been processed, the program will ask if you would like to add music to the video. Enter an arbitrary number of youtube links if you want to include the audio or enter f to skip
- note that if the music/audio is longer than the highlight video length, it will just result in a still image and the highlights video being dragged out longer. It's preferable to have music that is shorter than or equal in length to the highlight video.

### How to use - user
#### clip ($c)
- format: `$c xx:xx-yy:yy`. Note that times like 1:24 should be written as 01:24

#### clip and slow ($cs)
- format: `$cs xx:xx-yy:yy aa:aa-bb:bb`
- the time from `aa:aa-bb:bb` will be played right after the clip from `xx:xx-yy:yy` but in slow motion

#### download ($d) - dev only command
- format: `$d xx:xx-yy:yy`
- downloads the timestamp/clip to /DownloadedClips

#### fast forward ($f)
- format `$f xx:xx-yy:yy`
- plays the timestamp 50x faster than normal
