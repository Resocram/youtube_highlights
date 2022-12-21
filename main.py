import os
import pickle
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import youtube_dl
import datetime
import re
from timestamp import Timestamp
from moviepy.video.tools.subtitles import SubtitlesClip

CLIENT_SECRETS_FILE = os.path.dirname(
    os.path.realpath(__file__)) + "/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
NEW_LINE = '\n'
EMPTY_DELETE_MESSAGE = "Nothing to delete." + NEW_LINE
SLOW_MO_RATE = 0.3
FAST_FORWARD_RATE = 60

CLIP = "c"
CLIP_NO_MUSIC = "cnm"
CLOSED_CAPTIONING = "cc"
CLOSED_CAPTIONING_BLACK = "ccb"
DOWNLOAD = "d"
FAST_FORWARD = "f"
SLOW = "s"

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
    if not os.path.exists(directory + "/" + filename + ".mp4"):
        # 137 is 1920x1080 don't ask me how it just is
        ydl_opts = {'format': '137+bestaudio',
                    'outtmpl': directory + "/" + filename}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def downloadMusic(directory, filename, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': directory + "/" + filename + ".mp3"
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def getVideoId(url):
    return url[url.find("=")+1:len(url)]


def getComments(service, videoId):
    response = service.commentThreads().list(
        part="snippet",
        maxResults=100,
        videoId=videoId
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
    urls = []
    while True:
        command = input()
        if command[0] == 'd' and len(command) == 1:
            if len(urls) == 0:
                print(EMPTY_DELETE_MESSAGE)
            else:
                print("You deleted " + urls[-1] + NEW_LINE)
                del urls[-1]
        elif command[0] == 'f' and len(command) == 1:
            break
        else:
            urls.append(command)
            print("Added " + command)
        print("You currently have " + str(len(urls)) + " items." + NEW_LINE)

    return urls

def processMusicInput(clip_len):
    try:
        print("The final clip is " + str(clip_len) + " seconds, or " + str(datetime.timedelta(seconds=int(clip_len))) + ", if you would like to add an audio clip, enter the youtube link. Type d to delete previously added music. Otherwise, type f.")
        print("The music video should be equal or shorter in length than the video." + NEW_LINE + NEW_LINE)
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

def getAllTimestamps(comments):
    # Regex to get all matching comments
    timestamps = []
    for comment in comments:
        regex = "\$([a-z]{1,3})\s([0-9]{1,2}):([0-9]{2})-([0-9]{1,2}):([0-9]{2})"
        groups = re.findall(regex,comment)
        for group in groups:
            timestamps.append(Timestamp(*group))

    # Sort comments by chronological order of the first given timestamp in a comment
    # We can sort faster by sorting the timestamps upon insertion but that's too much effort and we don't have that many timestamps lol
    timestamps.sort()
    return timestamps

noMusicClips = []
globalTimestamps = []

def processClips(urls, currentDirectory):
    clips = []
    for idx, url in enumerate(urls):
        print("Handling video: " + str(idx + 1) + ", " + str(url) + NEW_LINE)
        videoId = getVideoId(url)

        downloadVideo(videoDirectory, videoId, url)
        comments = getComments(service, videoId)
        globalTimestamps = getAllTimestamps(comments)
        clipPath = videoDirectory + "/" + videoId + ".mp4"
        downloadsDirectory = currentDirectory + "/DownloadedClips"

        for idx, timestamp in enumerate(globalTimestamps):
            if timestamp.command == CLIP:
                clips.append(VideoFileClip(clipPath).subclip(timestamp.startTime, timestamp.endTime))
            elif timestamp.command == CLOSED_CAPTIONING:
                # TODO
                pass
            elif timestamp.command == DOWNLOAD:
                if not os.path.exists(downloadsDirectory):
                    os.mkdir(downloadsDirectory)
                downloadClip = VideoFileClip(clipPath).subclip(timestamp.startTime, timestamp.endTime)
                downloadClip.write_videofile(downloadsDirectory + "/" + str(timestamp.startTime) + str(timestamp.endTime) + ".mp4")
                downloadClip.close()
            elif timestamp.command == FAST_FORWARD:
                new_clip = VideoFileClip(clipPath).subclip(timestamp.startTime, timestamp.endTime)
                new_clip.audio = None
                clips.append(new_clip.fx(vfx.speedx, FAST_FORWARD_RATE))
            elif timestamp.command == CLIP_NO_MUSIC:
                # use an array to remember all the timestamps that we need to later remove music for
                noMusicClips.append(idx)
                clips.append(VideoFileClip(clipPath).subclip(timestamp.startTime, timestamp.endTime))
            elif timestamp.command == SLOW:
                clips.append(VideoFileClip(clipPath).subclip(timestamp.startTime, timestamp.endTime).fx(vfx.speedx, SLOW_MO_RATE))
    return clips

if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = getAuthenticatedService()
    print("Enter a list of youtube videos. Type d to delete previously added video. Type f when finished" + NEW_LINE)
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
    clips = processClips(urls, currentDirectory)
    finalClip = concatenate_videoclips(clips)

    musicAudio = processMusicInput(finalClip.duration)
    if musicAudio is not None:
        new_audioclip = CompositeAudioClip([finalClip.audio, musicAudio]) if finalClip.audio is not None else CompositeAudioClip([musicAudio])
        finalClip.audio = new_audioclip
        if len(noMusicClips) > 0:
            listOfNewNoMusicTimestamps = []
            nmClipsIdx = 0
            timerCounter = 0
            # finds the new timestamps in the output video that should not have music
            for timestamp in globalTimestamps:
                lengthClip = timestamp.getLengthOfTimestamp()
                if nmClipsIdx >= len(noMusicClips):
                    break
                # if the current clip is a no music clip (only supports no music on regular clips)
                if globalTimestamps[nmClipsIdx].startTime == timestamp.startTime and globalTimestamps[nmClipsIdx].endTime == timestamp.endTime:
                    listOfNewNoMusicTimestamps.append((timerCounter, timerCounter + lengthClip))
                    nmClipsIdx += 1
                if timestamp.command == SLOW:
                    timerCounter += lengthClip / SLOW_MO_RATE
                elif timestamp.command == FAST_FORWARD:
                    timerCounter += lengthClip / FAST_FORWARD_RATE
                else:
                    timerCounter += lengthClip


    finalClip.write_videofile(outputDirectory + "/" + "output.mp4")

