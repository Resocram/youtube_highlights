## Youtube Video Comments Highlight Tool

### Problem
Want to be able to generate a highlight video from youtube videos. Manually clipping these time stamps are super time costly and tiring.

### Solution
Get comments from youtube video that follow a specific time stamp format. Clip these time stamps and stitch them together to output a highlight video.

### Set Up
1. run `pip install -r requirements.txt`
2. add client_secrets.json file with the correct credentials (contact developer for more info)
    - fetching Youtube comments takes a dependency on this
    - can generate and download these secrets by going to Google Developer Console --> make sure that Youtube Data API v3 is enabled under "Enabled APIs & Services" --> create Credentials under "Credentials" --> download and paste this to client_secrets.json
3. download ffmpeg and add to environment variable (required by the library that is used to download YT video)
4. install imagemagick, follow the instructions shown [here](https://imagemagick.org/script/download.php)
5. run `python main.py`
6. prompted to authenticate on gmail
7. copy paste token to terminal

### How to use - dev
1. enter links, press enter after each link
2. press f to proceed
3. indicate y/n if the video URLs need to be downloaded from Youtube. In the case that you already have the videos on your local computer, ensure that they are in `/Videos` and that the name of the file is the exact same as the title of the video on Youtube. (e.g. Youtube Video Title == GX013489 == Video Name File == GX013489.mp4)
4. after the highlight video has been processed, the program will ask if you would like to add music to the video. Enter an arbitrary number of youtube links if you want to include the audio or enter f to skip

### How to use - user
#### captions ($cc)
- format: `$cc xx:xx-yy:yy "insert text here"`. Text within quotations can not contain " or $.

#### clip ($c)
- format: `$c xx:xx-yy:yy`. Note that times like 1:24 can be written as either 01:24 or 1:24

#### clip and no music($cnm)
- format: `$cnm xx:xx-yy:yy`. Play a clip without music

#### download ($d) - dev only command
- format: `$d xx:xx-yy:yy`
- downloads the timestamp/clip to /DownloadedClips

#### slow ($s)
- format: `$s xx:xx-yy:yy`. Plays the clip in slow motion

#### fast forward ($f)
- format `$f xx:xx-yy:yy`
- plays the timestamp 50x faster than normal

Certain features can be combined such as clip and slow:

#### clip and slow ($cs)
- format: `$c xx:xx-yy:yy $s aa:aa-bb:bb`
- the time from `aa:aa-bb:bb` will be played right after the clip from `xx:xx-yy:yy` but in slow motion
