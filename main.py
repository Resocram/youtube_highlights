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

CLIENT_SECRETS_FILE = os.path.dirname(
    os.path.realpath(__file__)) + "/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
NEW_LINE = '\n'
EMPTY_DELETE_MESSAGE = "Nothing to delete." + NEW_LINE


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
            credentials = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def downloadVideo(directory, filename, url):
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

# Only supports comments in this format $c xx:xx-yy:yy
def getTimestamps(comments):
    timestamps = []
    for comment in comments:
        try:
            if comment[0:2] == '$c':
                timestamp = (comment[3:8], comment[9:14])
                seconds = convertTimestampToSeconds(timestamp)
                if seconds is not None:
                    timestamps.append(seconds)
        except:
            pass

    print("Timestamps found: " + str(timestamps) + NEW_LINE)
    return timestamps

# Only supports comments in this format $cs xx:xx-yy:yy aa:aa-bb:bb
def getSlowMotionTimestamps(comments):
    timestamps = []
    for comment in comments:
        try:
            if comment[0:3] == '$cs':
                timestamp = ((comment[4:9], comment[10:15]), (comment[16:21], comment[22:27]))
                seconds = (convertTimestampToSeconds(timestamp[0]), convertTimestampToSeconds(timestamp[1]))
                if seconds is not None and seconds[0] is not None and seconds[1] is not None:
                    timestamps.append(seconds)
        except:
            pass

    print("Slow motion timestamps found: " + str(timestamps) + NEW_LINE)
    return timestamps

# Only supports comments in this format $d xx:xx-yy:yy
def getDownloadTimestamps(comments):
    timestamps = []
    for comment in comments:
        try:
            if comment[0:2] == '$d':
                timestamp = (comment[3:8], comment[9:14])
                seconds = convertTimestampToSeconds(timestamp)
                if seconds is not None:
                    timestamps.append(seconds)
        except:
            pass

    print("Download timestamps found: " + str(timestamps) + NEW_LINE)
    return timestamps

# Only supports comments in this format $f xx:xx-yy:yy
# f for fast forward
def getTimeLapseTimestamps(comments):
    timestamps = []

    for comment in comments:
        try:
            if comment[0:2] == '$f':
                timestamp = (comment[3:8], comment[9:14])
                seconds = convertTimestampToSeconds(timestamp)
                if seconds is not None:
                    timestamps.append(seconds)
        except:
            pass

    print("Time lapse timestamps found: " + str(timestamps) + NEW_LINE)
    return timestamps

def convertTimestampToSeconds(timestamp):
    try:
        startTime = int(timestamp[0][0:2])*60 + int(timestamp[0][3:5])
        endTime = int(timestamp[1][0:2])*60 + int(timestamp[1][3:5])
        return startTime, endTime
    except:
        pass

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

def processClips(urls, currentDirectory):
    clips = []
    for url in urls:
        videoId = getVideoId(url)

        downloadVideo(videoDirectory, videoId, url)
        comments = getComments(service, videoId)

        timestamps = getTimestamps(comments)
        for timestamp in timestamps:
            clips.append(VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[0], timestamp[1]))

        slowMotionTimeStamps = getSlowMotionTimestamps(comments)
        for timestamp in slowMotionTimeStamps:
            clips.append(VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[0][0], timestamp[0][1]))
            clips.append(VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[1][0], timestamp[1][1]).fx(vfx.speedx, 0.3))

        downloadTimeStamps = getDownloadTimestamps(comments)
        downloadsDirectory = currentDirectory + "/DownloadedClips"
        if not os.path.exists(downloadsDirectory):
            os.mkdir(downloadsDirectory)
        for timestamp in downloadTimeStamps:
            downloadClip = VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[0], timestamp[1])
            downloadClip.write_videofile(downloadsDirectory + "/" + str(timestamp[0]) + str(timestamp[1]) + ".mp4")
            downloadClip.close()

        timelapseTimeStamps = getTimeLapseTimestamps(comments)
        for timestamp in timelapseTimeStamps:
            clips.append(VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[0], timestamp[1]).fx(vfx.speedx, 50))

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
        new_audioclip = CompositeAudioClip([finalClip.audio, musicAudio])
        finalClip.audio = new_audioclip

    finalClip.write_videofile(outputDirectory + "/" + "output.mp4")