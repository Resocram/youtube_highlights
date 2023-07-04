console.log("hello from content.js")

const BUTTON_HEIGHT = 40
const BUTTON_WIDTH = 70
const BUTTON_GAP = 10
const COMMAND_PROMPT = "$"
const TEXT_ID = "highlight-textarea"
const GREEN = "#00ef5f"
const HOVER_GREEN = "#74ef00"

let CURRENT_COMMENT = {
    value: "",
    hasStartTime: false,
    currCommand: ""
}

// get triggered when user activates chrome extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const videoPlayer = document.querySelector("#player")
    if (videoPlayer) {
        const buttonContainer = getPopulatedButtonContainer()
        const textInput = getTextInput()

        // adds buttons and text input under the video
        videoPlayer.appendChild(buttonContainer)
        videoPlayer.appendChild(textInput)

        // shifts the Youtube video title downwards
        const titleContainer = document.getElementById("above-the-fold")
        titleContainer.style.marginTop = `${BUTTON_HEIGHT}px`
    }
})

function getPopulatedButtonContainer() {
    const buttonContainer = getButtonsContainer()
    const buttons = [
        getClipButton(0),
        getStartTimeButton(1),
        getEndTimeButton(2),
        getSlowButton(3),
        getCaptionButton(4),
        getFastButton(5),
        getClipNoMusicButton(6),
        getCommentButton(7),
    ]

    buttons.forEach((button) => {
        buttonContainer.appendChild(button)
    })

    return buttonContainer
}

// ============== BUTTON CREATION ==============
function getButtonsContainer() {
    const buttonsContainer = document.createElement(`div`)
    buttonsContainer.style.display = "flex"
    buttonsContainer.style.marginTop = "10px"

    return buttonsContainer
}

function getTextInput() {
    const textContainer = document.createElement(`div`)
    textContainer.style.display = "flex"
    textContainer.style.marginTop = `${BUTTON_HEIGHT + 10}px`

    const textInput = document.createElement(`input`)
    textInput.type = "text"
    textInput.id = TEXT_ID
    textInput.style.position = "absolute"
    textInput.style.width = "400px"
    textInput.style.padding = "10px"
    textInput.style.fontSize = "16px"

    textInput.addEventListener("change", (event) => {
        CURRENT_COMMENT = {
            value: event.target.value,
            hasStartTime: undefined,
            currCommand: ""
        }
    })

    textContainer.appendChild(textInput)

    return textContainer
}

function getClipButton(index) {
    return getCommandButton(index, 'Clip', 'c', true)
}

function getSlowButton(index) {
    return getCommandButton(index, 'Slow', 's', true)
}

function getCaptionButton(index) {
    return getCommandButton(index, 'Caption', 'cc', true)
}

function getClipNoMusicButton(index) {
    return getCommandButton(index, 'Clip no 🎵', 'cnm', true)
}

function getFastButton(index) {
    return getCommandButton(index, 'Fast', 'f', true)
}

function getStartTimeButton(index) {
    const startTimeButton = getStyledButton(index)
    startTimeButton.innerHTML = "Start"

    startTimeButton.addEventListener('click', addStartTime)

    return startTimeButton
}

function getEndTimeButton(index) {
    const endTimeButton = getStyledButton(index)
    endTimeButton.innerHTML = "End"

    endTimeButton.addEventListener('click', addEndTime)

    return endTimeButton
}

function getCommentButton(index) {
    const commentButton = getStyledButton(index)
    commentButton.innerHTML = "Post"

    commentButton.addEventListener('click', () => {
        // Triggers Youtube UI to make their "Comment" button visible
        document.querySelector("#placeholder-area").click()

        // inputs comment content, making the "Comment" button clickable
        const commentInput = document.querySelector("#contenteditable-root")
        commentInput.value = CURRENT_COMMENT.value
        commentInput.innerHTML = CURRENT_COMMENT.value
        const event = new Event('input', { bubbles: true })
        commentInput.dispatchEvent(event)

        // click "Comment" button to post
        document.querySelector("#submit-button").click()

        CURRENT_COMMENT.value = ""
        CURRENT_COMMENT.currCommand = ""
        CURRENT_COMMENT.hasStartTime = false
        updateTextInput()
    })

    return commentButton
}

// ============== LOGIC/ABSTRACTION ==============

function computeButtonPosition(index) {
    return (index * BUTTON_WIDTH) + (index * BUTTON_GAP)
}

function addStartTime() {
    const currTime = getVideoCurrTime()
    CURRENT_COMMENT.value += `${currTime}-`
    if (CURRENT_COMMENT.hasStartTime) {
        CURRENT_COMMENT = {
            ...CURRENT_COMMENT,
            value: `${CURRENT_COMMENT.currCommand}${currTime}-`,
        }
    }
    CURRENT_COMMENT.hasStartTime = true
    updateTextInput()
}

function addEndTime() {
    CURRENT_COMMENT.value += `${getVideoCurrTime()} `
    updateTextInput()
}

function addCommand(command) {
    const formattedCommand = `${COMMAND_PROMPT}${command} `
    CURRENT_COMMENT.value += formattedCommand
    CURRENT_COMMENT.currCommand = formattedCommand
    updateTextInput()
}

function getStyledButton(index, color, hoverColor) {
    const button = document.createElement(`button`)
    button.style.position = "absolute"
    button.style.left = `${computeButtonPosition(index)}px`
    button.style.borderRadius = "8px"
    button.style.width = `${BUTTON_WIDTH}px`
    button.style.height = `${BUTTON_HEIGHT}px`
    button.style.outline = "none"
    button.style.boxShadow = "none"
    button.style.cursor = "pointer"
    button.style.fontWeight = "bold"
    button.style.backgroundColor = color || "#008eef"

    button.addEventListener('mouseenter', () => {
        button.style.backgroundColor = hoverColor || "#00b6ef"
    })

    button.addEventListener('mouseleave', () => {
        button.style.backgroundColor = color || "#008eef"
    })
    return button
}

function getCommandButton(index, name, command, isCommand) {
    let button = getStyledButton(index)
    if (isCommand) {
        button = getStyledButton(index, GREEN, HOVER_GREEN)
    }
    button.innerHTML = name

    button.addEventListener('click', () => {
        addCommand(command)
        // if the current command is the second command
        // turn off the functionality that replaces the command + start time
        if (CURRENT_COMMENT.hasStartTime) {
            CURRENT_COMMENT.hasStartTime = false
            CURRENT_COMMENT.currCommand = ""
        }
    })

    return button
}

function getVideoCurrTime() {
    const currTimeInSeconds = Math.floor(document.getElementsByTagName("video")[0].currentTime)

    const minutes = parseInt(currTimeInSeconds / 60, 10)
    let seconds = (currTimeInSeconds % 60).toFixed(0)
    seconds = seconds < 10 ? seconds.toString().padStart(2, '0') : seconds

    return `${minutes}:${seconds}`
}

function updateTextInput() {
    const input = document.querySelector(`#${TEXT_ID}`)
    input.value = CURRENT_COMMENT.value
}

// ============== HOT KEYS ==============
document.addEventListener('keyup', (e) => {
    // Ctrl + alt + S
    if (e.ctrlKey && e.altKey && e.which == 83) {
        addStartTime()
    }
    // Ctrl + alt + E
    if (e.ctrlKey && e.altKey && e.which == 69) {
        addEndTime()
    }
    // Ctrl + alt + C
    if (e.ctrlKey && e.altKey && e.which == 67) {
        addCommand('c')
    }
})