# Written by Jason K. in Oct 2024
# Contact: https://www.youtube.com/@jasonkitoow

from tkinter import colorchooser, Tk, Frame, Button, Label, BOTTOM, RIGHT, LEFT
import numpy as np
import time
import pyautogui
import cv2
import easyocr
import pykakasi

# UI setting
CONSOLE_SHOW = False
TITLE = "Kanji > Hiragana 4 subtitles"
LABEL_FONT = ("Arial", 18)
WORD_VERTICAL_COLORS = ["gray75", "gray73", "gray70", "gray69", "gray68","gray67", "gray66", "gray65", "gray64", "gray63", "gray62","gray61", "gray60","gray59", "gray58","gray57", "gray56","gray55", "gray54", "gray53" ]
WORD_HORIZONTAL_COLORS = ["cadetblue1", "burlywood1", "beige", "azure1", "aquamarine1", "greenyellow", "khaki1", "plum1", "thistle1", "steelblue1" ]
WORD_VERTICAL_COUNT = len(WORD_VERTICAL_COLORS)
WORD_HORIZONTAL_COUNT = len(WORD_HORIZONTAL_COLORS)
INTRO = [""] * WORD_HORIZONTAL_COUNT
INTRO[0] = "[ Subtitle Area ]"
INIT_SCREEN_SIZE = '683x427'

# OpenCV setting
DELAY_IMAGE_PROCESSING = 0.1
DELAY_UI = 0.01
COLOR_THRESHOLD = 21
IMAGE_PROCCESSING_BLUR = (3,3)

# User setting
selectedArea = None
selectedColor = None
colorMin = None
colorMax = None

# State
runCheck1 = False
runCheck2 = False
runTranslate = False
runWindow = True

# UI element
root = Tk()
buttonArea = None
buttonColor = None
buttonCheck1 = None
buttonCheck2 = None
buttonStart = None
labelVecticalArr = []
labelHorizontalArr = []

def close_window():
    global runWindow, runTranslate, runCheck1, runCheck2
    runWindow = False
    runTranslate = False
    runCheck1 = False
    runCheck2 = False
    cv2.destroyAllWindows()

def on_enter(event):
    if event != None and event.widget != root:
        return
    global buttonStart
    if buttonArea != None:
        return
    add_button()
    bottomframe.config(background='systemWindowBackgroundColor')
    root.config(highlightbackground="black", highlightthickness = 1)
    root.update()

def on_leave(event):
    if event != None and event.widget != root:
        return
    global buttonArea, buttonColor, buttonCheck1, buttonCheck2, buttonStart, runTranslate
    if buttonArea == None or not runTranslate:
        return
    buttonArea.pack_forget()
    buttonColor.pack_forget()
    buttonCheck1.pack_forget()
    buttonCheck2.pack_forget()
    buttonStart.pack_forget()
    buttonArea = None
    buttonColor = None
    buttonCheck1 = None
    buttonCheck2 = None
    buttonStart = None
    root.config(highlightbackground="black", highlightthickness = 0)
    bottomframe.config(bg='systemTransparent')
    root.update()

def refresh_button():
    global buttonArea, buttonColor, buttonCheck1, buttonCheck2, buttonStart
    if buttonArea == None:
        return

    areaButStr = "Area: [Pls capture!]" if selectedArea == None else "Area: [" + str(selectedArea[0]) + ", " + str(selectedArea[1]) + "] > [" + str(selectedArea[0] + selectedArea[2]) + ", " + str(selectedArea[1] + selectedArea[3]) + "]"
    actionButStr = "Stop" if runTranslate else "Start"
    colorButStr = "Color: [Pls select!]" if selectedColor == None else "Color: [" + str(selectedColor[0]) + ", " + str(selectedColor[1]) + ", "  + str(selectedColor[2]) + "]"
    checking1ButStr = "Close 1" if runCheck1 else "Preview 1"
    checking2ButStr = "Close 2" if runCheck2 else "Preview 2"

    areaButFg = "grey" if runTranslate else ("red" if selectedArea == None else "black")
    colorButFg = "grey" if runTranslate else ("red" if selectedColor == None else "black")
    checking1ButFg = "grey" if selectedArea == None or selectedColor == None or runTranslate else "black"
    checking2ButFg = "grey" if selectedArea == None or selectedColor == None or runTranslate else "black"
    actionButBg = "grey" if selectedArea == None or selectedColor == None or runCheck1 or runCheck2 else "black"

    buttonArea.config(text=areaButStr, fg = areaButFg)
    buttonColor.config(text=colorButStr, fg = colorButFg)
    buttonCheck1.config(text=checking1ButStr, fg = checking1ButFg)
    buttonCheck2.config(text=checking2ButStr, fg = checking2ButFg)
    buttonStart.config(text=actionButStr, fg = actionButBg)

def add_button():
    global buttonArea, buttonColor, buttonCheck1, buttonCheck2, buttonStart
    buttonStart = Button(bottomframe, command = toggle_run)
    buttonStart.pack(side = RIGHT)
    buttonArea = Button(bottomframe, command = select_area)
    buttonArea.pack(side = LEFT)
    buttonColor = Button(bottomframe, command = choose_color)
    buttonColor.pack(side = LEFT)
    buttonCheck1 = Button(bottomframe, command = toggle_check1)
    buttonCheck1.pack(side = LEFT)
    buttonCheck2 = Button(bottomframe, command = toggle_check2)
    buttonCheck2.pack(side = LEFT)
    refresh_button()

def toggle_run():
    if selectedArea == None or selectedColor == None or runCheck1 or runCheck2:
        return
    global runTranslate
    runTranslate = not runTranslate
    if runTranslate:
        labelVecticalArr[0].config(text = "Scanning...")
        on_leave(None)
    else:
        if labelVecticalArr[0].cget("text") == "Scanning...":
            labelVecticalArr[0].config(text = "")
    refresh_button()

def toggle_check1():
    if selectedArea == None or selectedColor == None or runTranslate:
        return
    global runCheck1
    runCheck1 = not runCheck1
    cv2.destroyWindow("Preview 1")
    refresh_button()

def toggle_check2():
    if selectedArea == None or selectedColor == None or runTranslate:
        return
    global runCheck2
    runCheck2 = not runCheck2
    cv2.destroyWindow("Preview 2")
    refresh_button()

def select_area():
    if runTranslate:
        return
    root.config(bg='pink') # reminder: flashing
    root.update()
    global selectedArea
    # reminder: the area captured does not exactly fit into Mac's coordinates due to menu bar
    selectedArea = [root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()]
    refresh_button()
    root.config(bg='systemTransparent')

def choose_color():
    if runTranslate:
        return
    root.wm_attributes("-topmost", False) # reminder: avoid color picker covered
    c = colorchooser.askcolor(title ="Choose color")[0]
    root.wm_attributes("-topmost", True)
    if c == None:
        return
    global selectedColor, colorMin, colorMax
    selectedColor = c
    refresh_button()
    colorMin = np.array([max(c[2] - COLOR_THRESHOLD, 0), max(c[1] - COLOR_THRESHOLD, 0), max(c[0] - COLOR_THRESHOLD, 0)], np.uint8)
    colorMax = np.array([min(c[2] + COLOR_THRESHOLD, 255), min(c[1] + COLOR_THRESHOLD, 255), min(c[0] + COLOR_THRESHOLD, 255)], np.uint8)

def init_UI():
    global bottomframe, textframe
    #root.overrideredirect(False)
    #root.minsize(width=500, height=260)
    root.title(TITLE)
    root.geometry(INIT_SCREEN_SIZE)
    root.wm_attributes("-transparent", True)
    root.wm_attributes("-topmost", True)
    root.config(bg='systemTransparent')
    root.config(highlightbackground="black", highlightthickness = 1)
    root.bind("<Enter>", on_enter)
    root.bind("<Leave>", on_leave)
    root.protocol("WM_DELETE_WINDOW", close_window)

    bottomframe = Frame(root)
    add_button()
    bottomframe.pack(side=BOTTOM, fill="x")

    textframe = Frame(root)
    textframe.pack(side = BOTTOM)
    for i in range(0, WORD_HORIZONTAL_COUNT):
        labelHorizontalArr.append(Label(textframe, text = INTRO[i], font=LABEL_FONT, fg=WORD_HORIZONTAL_COLORS[i], bg='systemTransparent'))
        labelHorizontalArr[i].pack(side = LEFT)
    for i in range(0, WORD_VERTICAL_COUNT):
        labelVecticalArr.append(Label(root, font=LABEL_FONT, fg=WORD_VERTICAL_COLORS[i], bg='systemTransparent'))
        labelVecticalArr[i].pack(anchor="w", side = BOTTOM)

init_UI()

ocrReader = easyocr.Reader(['ja']) # Image to Text
jpTranslator = pykakasi.kakasi() # Kanji to Hiragana

lastTriggerTime = 0
lastResultStr = ""
wordsAccumlated = [''] * WORD_VERTICAL_COUNT
while runWindow:
    time.sleep(DELAY_UI)
    root.update()

    if not runTranslate and not runCheck1 and not runCheck2:
        continue
    if time.time() - lastTriggerTime < DELAY_IMAGE_PROCESSING:
        continue

    img = pyautogui.screenshot(region=(tuple(selectedArea)))
    frame = np.array(img)
    frameBgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frameFiltered = cv2.inRange(frameBgr, colorMin, colorMax)
    frameBlurred = cv2.GaussianBlur(frameFiltered, IMAGE_PROCCESSING_BLUR, 0)
    if runCheck1:
        cv2.imshow("Preview 1", frame)
    if runCheck2:
        cv2.imshow("Preview 2", frameFiltered)
    #cv2.imshow("Preview 3 ", frameBlurred)

    if not runTranslate:
        continue

    result = ocrReader.readtext(frameBlurred)
    resultStr = "".join([result[i][1] for i in range(len(result))])
    if resultStr and resultStr != lastResultStr:
        lastResultStr = resultStr
        if CONSOLE_SHOW:
            print(resultStr)

        interpretedItems = jpTranslator.convert(resultStr)
        translatedWords = []
        i = 0

        # show new translated words to the horizontal label list
        for item in interpretedItems:
            if i == WORD_HORIZONTAL_COUNT:
                break
            word = item['orig'] + " : " + item['hira'] + "" if item['orig'] != item['hira'] and item['orig'] != item['kana'] else ""
            if word == "":
                continue
            labelHorizontalArr[i].config(text = word)
            translatedWords.append(word)
            i += 1
        for j in range(i, WORD_HORIZONTAL_COUNT):
            labelHorizontalArr[j].config(text = "")
        root.update()

        # append new translated words to the vertical label list
        if len(translatedWords) > 0:
            newWords = set(translatedWords) - set(wordsAccumlated)
            wordsAccumlated = list(newWords) + wordsAccumlated
            wordsAccumlated = wordsAccumlated[:WORD_VERTICAL_COUNT]
            for i in range(0, WORD_VERTICAL_COUNT):
                labelVecticalArr[i].config(text = wordsAccumlated[i])
            root.update()
    
    lastTriggerTime = time.time()