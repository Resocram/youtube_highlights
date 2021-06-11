import pytube
import os
import pickle
from moviepy.editor import VideoFileClip, concatenate_videoclips
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRETS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
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
 
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def downloadVideo(directory,filename,url):
    print("Downloading " + url) 
    pytube.YouTube(url).streams.get_highest_resolution().download(output_path = directory, filename = filename)
    print("Finished downloading " + url)

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
    for i in range(0,numComments):
        comments.append(items[i]['snippet']['topLevelComment']['snippet']['textOriginal'])

    print("Comments found: " + str(comments))
    return comments


def getTimestamps(comments):
    timestamps = []
    for comment in comments:
        # Only supports in comments in this format $c xx:xx-yy:yy
        try:
            if comment[0] == '$' and comment[1] == 'c':
                timestamp = (comment[3:8],comment[9:14])
                seconds = convertTimestampToSeconds(timestamp)
                if seconds is not None:
                    timestamps.append(seconds)
        except:
            pass

    print("Timestamps found: " + str(timestamps))
    return timestamps


def convertTimestampToSeconds(timestamp):
    try:
        startTime = int(timestamp[0][0:2])*60 + int(timestamp[0][3:5])
        endTime = int(timestamp[1][0:2])*60 + int(timestamp[1][3:5])
        return startTime, endTime
    except:
        pass


if __name__ == "__main__":
    

    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
    print("Enter a list of youtube videos. Type d to delete previously added video. Type f when finished")
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    videoDirectory = currentDirectory + "/Videos"
    outputDirectory = currentDirectory + "/Output"
    if not os.path.exists(videoDirectory):
        os.mkdir(videoDirectory)
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)

    urls=[]
    clips=[]

    while True:
        command = input()
        if command[0] == 'd' and len(command) == 1:
            if len(urls) == 0:
                print("Nothing to delete.")
            else:
                print("You deleted " + urls[-1])
                del urls[-1]
        elif command[0] == 'f' and len(command) == 1:
            break
        else:
            urls.append(command)
            print("Added " + command)
        print("You currently have " + str(len(urls)) + " items.")
    
    for url in urls:
        videoId = getVideoId(url)

        downloadVideo(videoDirectory,videoId, url)
        comments = getComments(service, videoId)
        timestamps = getTimestamps(comments)
        for timestamp in timestamps:
            clips.append(VideoFileClip(videoDirectory + "/" + videoId + ".mp4").subclip(timestamp[0],timestamp[1]))

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(outputDirectory + "/" + "output.mp4")