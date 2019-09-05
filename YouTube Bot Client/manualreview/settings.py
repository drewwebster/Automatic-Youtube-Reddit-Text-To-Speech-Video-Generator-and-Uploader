from datetime import timedelta
import os

wordsPerMinute = 175 # avg is between 125-150, assuming 125 for now
timeBetweenCommentThread = timedelta(seconds=1)
recommendedLength = timedelta(minutes=10)
currentPath = os.path.dirname(os.path.realpath(__file__))

thumbnailpath = currentPath + "/Thumbnails"
scriptsaves = currentPath + "/Scriptsaves"