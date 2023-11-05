import os
import pickle
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from yt_dlp import YoutubeDL
import datetime
import re
from timestamp import Timestamp
from moviepy.video.tools.subtitles import SubtitlesClip

CLIENT_SECRETS_FILE = os.path.dirname(
    os.path.realpath(__file__)) + "/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
NEW_LINE = '\n ========================================'
EMPTY_DELETE_MESSAGE = "Nothing to delete." + NEW_LINE
SLOW_MO_RATE = 0.3
FADEWAY_TIME = 3
FAST_FORWARD_RATE = 60
MUSIC_LOUDNESS_FACTOR = 0.5

CLIP = "c"
CLIP_NO_MUSIC = "cnm"
CLOSED_CAPTIONING = "cc"
DOWNLOAD = "d"
FAST_FORWARD = "f"
SLOW = "s"

# FLAGS
VIDEO_FILE_NAME_IS_YT_TITLE = False

def getAuthenticatedService():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def downloadVideo(directory, filename, url):
    if VIDEO_FILE_NAME_IS_YT_TITLE:
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            filename = info_dict.get('title', None)

    if not os.path.exists(directory + "/" + filename + ".mp4"):
        ydl_opts = {'format_sort': ['res:1080', 'ext:mp4:m4a'],
                    'outtmpl': directory + "/" + filename}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    return filename

def downloadMusic(directory, filename, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': True,
        'outtmpl': directory + "\\" + filename + ".mp3"
        }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.cache.remove()
        try:
            ydl.download([url])
        except Exception as error:
            pass


def getVideoId(url):
    return url[url.find("=")+1:len(url)]


def getComments(service, videoId):
    response = service.commentThreads().list(
        part="snippet",
        maxResults=100,
        videoId=videoId,
    ).execute()

    numComments = response['pageInfo']['totalResults']
    items = response['items']
    comments = []
    for i in range(0, numComments):
        comments.append(items[i]['snippet']
                        ['topLevelComment']['snippet']['textOriginal'])

    print("Comments found: " + str(comments) + NEW_LINE)
    return comments

def processUrlInput():
    playlistURL = input()
    # added to avoid "Incomplete data received" exception (https://github.com/yt-dlp/yt-dlp/issues/8206#issuecomment-1740223250)
    ydl_opts = {
        "ignoreerrors": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlistURL, download=False)
        videosInPlaylist = playlist_info["entries"]

    # pop in order to avoid this issue: https://github.com/yt-dlp/yt-dlp/issues/8206#issuecomment-1735924571
    # videosInPlaylist.pop()
    urls = [video["webpage_url"] for video in videosInPlaylist]
    return urls

def processMusicInput(clip_len):
    try:
        print("The final clip is " + str(clip_len) + " seconds, or " + str(datetime.timedelta(seconds=int(clip_len))) + ", if you would like to add an audio clip, enter the youtube link. Type d to delete previously added music. Otherwise, type f.")
        urls = []
        while True:
            command = input()
            if command[0] == 'f' and len(command) == 1:
                break
            if command[0] == 'd' and len(command) == 1:
                if len(urls) == 0:
                    print(EMPTY_DELETE_MESSAGE)
                else:
                    print("You deleted " + urls[-1] + NEW_LINE)
                    del urls[-1]
            else:
                urls.append(command)
            print("You currently have " + str(len(urls)) + " items." + NEW_LINE)

        audioClips = []
        for url in urls:
            videoId = getVideoId(url)
            downloadMusic(musicDirectory, videoId, url)
            audioClips.append(AudioFileClip(musicDirectory + "/" + videoId + ".mp3"))
        return concatenate_audioclips(audioClips) if len(audioClips) > 0 else None

    except Exception as e:
        print("Problem in music processing")
        print(e)
        return None

# Get all the timestamp in the comments if it matches
# Returns a tuple of captions of timestamps, timestamps_cc, timestamps_f
def getAllTimestamps(comments):
    # Regex to get all matching comments
    timestamps = []
    timestamps_cc = []
    timestamps_f = []
    for comment in comments:
        regex = "\$([a-z]{1,3})\s([0-9]{1,2}):([0-9]{2})-([0-9]{1,2}):([0-9]{2})\s*\"*([^$\"]*)\"*"
        groups = re.findall(regex,comment)
        for group in groups:
            if group[0] == CLOSED_CAPTIONING:
                timestamps_cc.append(Timestamp(*group))
            elif group[0] == FAST_FORWARD:
                timestamps_f.append(Timestamp(*group))
            else:
                timestamps.append(Timestamp(*group))

    # Sort comments by chronological order of the first given timestamp in a comment
    # We can sort faster by sorting the timestamps upon insertion but that's too much effort and we don't have that many timestamps lol
    timestamps_cc.sort()
    timestamps_f.sort()
    timestamps.sort()

    return (timestamps,timestamps_cc,timestamps_f)


def processClips(urls, currentDirectory):
    clips = []
    noMusicIndices = []
    for idx, url in enumerate(urls):
        print("Handling video: " + str(idx + 1) + ", " + str(url) + NEW_LINE)
        videoId = getVideoId(url)
        videoTitle = downloadVideo(videoDirectory, videoId, url)
        comments = getComments(service, videoId)
        timestamps,timestamps_cc,timestamps_f = getAllTimestamps(comments)
        pathID = videoTitle if VIDEO_FILE_NAME_IS_YT_TITLE else videoId
        clipPath = videoDirectory + "/" + pathID + ".mp4"

        downloadsDirectory = currentDirectory + "/DownloadedClips"
        subs = []
        videoClip = VideoFileClip(clipPath)
        for timestamp_cc in timestamps_cc:
            subs.append(((timestamp_cc.startTime,timestamp_cc.endTime), timestamp_cc.cc))
        if len(timestamps_cc) != 0:
            generator = lambda txt: TextClip(txt, font='Trebuchet MS', fontsize=60, color="white",stroke_color = "black",stroke_width = 2)
            subtitles = SubtitlesClip(subs, generator)
            videoClip = CompositeVideoClip([videoClip, subtitles.set_position(("center",0.9),relative=True)])

        for timestamp in timestamps:
            if timestamp.command == CLIP:
                clips.append(videoClip.subclip(timestamp.startTime, timestamp.endTime))
            elif timestamp.command == DOWNLOAD:
                if not os.path.exists(downloadsDirectory):
                    os.mkdir(downloadsDirectory)
                downloadClip = videoClip.subclip(timestamp.startTime, timestamp.endTime)
                downloadClip.write_videofile(downloadsDirectory + "/" + str(timestamp.startTime) + str(timestamp.endTime) + ".mp4")
                downloadClip.close()
            elif timestamp.command == CLIP_NO_MUSIC:
                noMusicIndices.append(len(clips))
                clips.append(videoClip.subclip(timestamp.startTime, timestamp.endTime))
            elif timestamp.command == SLOW:
                clips.append(videoClip.subclip(timestamp.startTime, timestamp.endTime).fx(vfx.speedx, 0.3))
        for timestamp_f in timestamps_f:
            new_clip = videoClip.subclip(timestamp_f.startTime, timestamp_f.endTime)
            new_clip.audio = None
            clips.append(new_clip.fx(vfx.speedx, 60))
    return clips, noMusicIndices

def processNoMusicIndices(clips, noMusicIndices):
    duration = 0
    noMusicIndex = 0
    i = 0
    durations = []
    if len(noMusicIndices) == 0:
        return durations
    while i <= noMusicIndices[-1]:
        if i == noMusicIndices[noMusicIndex]:
             durations.append((duration,duration+clips[i].duration))
             noMusicIndex +=1
        duration += clips[i].duration
        i += 1
    return durations

def removeNoMusicDurations(musicAudio,noMusicDurations):
    for noMusicDuration in noMusicDurations:
        start = noMusicDuration[0]
        end = noMusicDuration[1]
        musicAudio =  concatenate_audioclips([musicAudio.subclip(0,start),musicAudio.subclip(start,end).fx(afx.volumex,0),musicAudio.subclip(end,musicAudio.duration)])
    return musicAudio

if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = getAuthenticatedService()

    print("Enter a Youtube Playlist." + NEW_LINE)
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    videoDirectory = currentDirectory + "/Videos"
    outputDirectory = currentDirectory + "/Output"
    musicDirectory = currentDirectory + "/Music"
    if not os.path.exists(videoDirectory):
        os.mkdir(videoDirectory)
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)
    if not os.path.exists(musicDirectory):
        os.mkdir(musicDirectory)

    urls = processUrlInput()

    print("Do these videos need to be downloaded from Youtube? y or n" + NEW_LINE)
    while True:
        command = input()
        if command[0] == 'y' and len(command) == 1:
            break
        if command[0] == 'n' and len(command) == 1:
            VIDEO_FILE_NAME_IS_YT_TITLE = True
            break
        else:
            print("input did not match y or n, will proceed by downloading videos from YT." + NEW_LINE)
            break

    clips, noMusicIndices = processClips(urls, currentDirectory)
    noMusicDurations = processNoMusicIndices(clips,noMusicIndices)
    finalClip = concatenate_videoclips(clips)
    musicAudio = processMusicInput(finalClip.duration)
    if musicAudio is not None:
        musicAudio = musicAudio.fx(afx.volumex,MUSIC_LOUDNESS_FACTOR)
        if len(noMusicDurations) != 0:
            musicAudio = removeNoMusicDurations(musicAudio,noMusicDurations)
        new_audioclip = CompositeAudioClip([finalClip.audio, musicAudio]) if finalClip.audio is not None else CompositeAudioClip([musicAudio])
        finalClip.audio = new_audioclip.subclip(finalClip.start,finalClip.end)
    finalClip.audio = finalClip.audio.fx(afx.audio_fadeout,FADEWAY_TIME)
    finalClip.write_videofile(outputDirectory + "/" + "output.mp4",threads=8)

