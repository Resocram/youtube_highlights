class Timestamp:
    def __init__(self,command,startMin,startSec,endMin,endSec):
        self.command = command
        self.startMin = startMin
        self.startSec = startSec
        self.endMin = endMin
        self.endSec = endSec
        self.startTime, self.endTime = self.convertTimestampToSeconds()

    # Custom comparator when comparing timestamps
    def __lt__(self,other):
        return self.startTime < other.startTime

    # Custom comparator to define equality of timestamps
    def __eq__(self,other):
        return self.command == other.command and self.startTime == other.startTime and self.endTime == other.endTime

    # Command that gets outputted when print() or str() is called
    def __str__(self):
        return "Command is " + self.command + " from " + str(self.startTime) + " to " + str(self.endTime)

    # Time is given in a:b to c:d
    def convertTimestampToSeconds(self):
        SECONDS_IN_MINUTES = 60
        try:
            startTime = int(self.startMin)*SECONDS_IN_MINUTES+int(self.startSec)
            endTime = int(self.endMin)*SECONDS_IN_MINUTES+int(self.endSec)
            return startTime, endTime
        except:
            pass

    def getLengthOfTimestamp(self):
        timestampInSeconds = self.convertTimestampToSeconds()
        return timestampInSeconds[1] - timestampInSeconds[0]