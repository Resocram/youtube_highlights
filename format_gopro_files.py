import os

PATH = './Videos'

def getListOfFiles():
    videoDir = os.scandir(PATH)
    files = []
    for file in videoDir:
        if file.is_file():
            files.append({
                'fileObj': file,
                'name': file.name
            })

    videoDir.close()

    return files

# assuming that files are always formatted like "GX<YY><XXXX>"
# create an object where all the keys are <XXXX>
# e.g. {
#   "3656": [
#       "GX013565",
#       "GX023565"
#   ]
# }
def getGroupedRecordings(files):
    res = {}
    for file in files:
        recordingID = int(file["name"][4:8])
        if recordingID in res.keys():
            res[recordingID].append(file["name"])
        else:
            res[recordingID] = [file["name"]]
    return res



if __name__ == "__main__":
    files = getListOfFiles()

    groupedRecordings = getGroupedRecordings(files)
    fileCounter = 1
    # the keys should be in sorted order (windows default)
    for key in groupedRecordings.keys():
        for subrecordingID in groupedRecordings[key]:
            os.rename("{}/{}".format(PATH, subrecordingID), "{}/{}".format(PATH, str(fileCounter) + subrecordingID))
            fileCounter += 1
