## Youtube Video Comments Chrome Extension

### Problem
Outlined here: https://github.com/Resocram/youtube_highlights/issues/22
tldr: it is really tedious and annoying to manually go through the flow of commenting a specific highlight.

### Solution
Create a UI that makes commenting on Youtube videos easier. This extension is not published so this is an extension that is loaded locally.

### Set Up
1. Open up Chrome/Opera and navigate to chrome://extensions or opera://extensions
2. Click `Devekoper mode` top right
3. Click `Load unpacked` and select the folder that contains the extension (`/ChromeExtensions/Commenter/`)

### How to use
1. On a Youtube video, click `Extensions` on the browser and select this chrome extension
2. The UI should show up under the video

- Green buttons represent commands (e.g. `$c`, `$s`, `$cc`)
- Blue buttons represent all other commands (e.g. start time, end time, and post)
- One unintuitive feature is that when a user has started with a command and a start time but has NOT selected the end time yet, and clicks start time again, the current WIP comment gets replaced with the current command + the new start time. This is intended for the use case where the user is watching the video and presses `$c xx:yy-` at the beginning of every single clip (even if it is not a highlight). Once they find out that it is not highlight worthy, they do not have to backtrack their current comment but can simply just select the new start time of the next rally/clip and continue. This features works poorly when there is more than one command (e.g. BOTH clip and slow (`$c xx:yy-aa:bb $s cc:dd-jj:kk`))
- The following keyboard shortcuts exists:
    - Clip: ctrl + alt + c
    - Start: ctrl + alt + s
    - End: ctrl + alt + e

