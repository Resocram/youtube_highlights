console.log("hello from background.js")

chrome.action.onClicked.addListener(buttonClicked)

function buttonClicked(tab) {
    chrome.tabs.sendMessage(tab.id, "Call Commenter UI")
}