from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe
from math import hypot
import numpy as np
import matplotlib.pyplot as plt



app = Flask(__name__)

cap = cv2.VideoCapture(0)
initHand = mediapipe.solutions.hands
mainHand = initHand.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
draw = mediapipe.solutions.drawing_utils

ACCENT_BGR  = (124, 168, 232)   # #e8a87c — warm peach accent
SOFT_WHITE  = (238, 241, 243)   # #f3f1ee — off-white
JOINT_LINE  = (190, 190, 190)   # subtle grey for skeleton connections
JOINT_POINT = (220, 220, 220)   # soft white for joint dots

LANDMARK_STYLE   = draw.DrawingSpec(color=JOINT_POINT, thickness=2, circle_radius=3)
CONNECTION_STYLE = draw.DrawingSpec(color=JOINT_LINE,  thickness=1)


def fingers(landmarks):
    fingerTips = []
    tipIds = [4, 8, 12, 16, 20]


    if landmarks[tipIds[0]][1] > landmarks[tipIds[0] - 1][1]:
        fingerTips.append(1)
    else:
        fingerTips.append(0)


    for id in range(1, 5):
        if landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 3][2]:
            fingerTips.append(1)
        else:
            fingerTips.append(0)

    return fingerTips


def handLandmarks(colorImg):
    landmarkList = []

    landmarkPositions = mainHand.process(colorImg)
    landmarkCheck = landmarkPositions.multi_hand_landmarks
    if landmarkCheck:
        for hand in landmarkCheck:
            draw.draw_landmarks(colorImg, hand, initHand.HAND_CONNECTIONS,
                                LANDMARK_STYLE, CONNECTION_STYLE)
            for index, landmark in enumerate(hand.landmark):
                h, w, c = colorImg.shape
                centerX, centerY = int(landmark.x * w), int(landmark.y * h)
                landmarkList.append([index, centerX, centerY])
    return landmarkList


def draw_fingertip_overlay(img, tips):
    for i in range(len(tips) - 1):
        cv2.line(img, tips[i], tips[i + 1], ACCENT_BGR, 2, cv2.LINE_AA)
    for (px, py) in tips:
        cv2.circle(img, (px, py), 7, SOFT_WHITE,  -1, cv2.LINE_AA)
        cv2.circle(img, (px, py), 4, ACCENT_BGR,  -1, cv2.LINE_AA)


lengththindlist = []
lengthindmidlist = []
lengthmidrinlist = []
lengthrinpinlist = []
lengthrinthulist = []
lengthmidthulist = []

current_mudra_name = None

MUDRA_INFO = {
    "Pataka":        {"display": "Patāka",        "devanagari": "पताका",       "emoji": "✋",  "description": "The flag — depicts clouds, forest, river, blessing, and denial."},
    "Tripataka":     {"display": "Tripatāka",     "devanagari": "त्रिपताक",     "emoji": "\U0001F590", "description": "Three parts of a flag — symbolizes crown, tree, vajra, and arrow."},
    "Shikaram":      {"display": "Śikhara",       "devanagari": "शिखर",        "emoji": "\U0001F44D", "description": "The spire — represents the bow, a pillar, silence, and the beloved."},
    "Ardhapataka":   {"display": "Ardhapatāka",   "devanagari": "अर्धपताक",     "emoji": "\U0001FAF1", "description": "Half flag — depicts leaves, riverbank, knife, and a tower."},
    "Kartharimukha": {"display": "Karthārīmukha", "devanagari": "कर्तरीमुख",    "emoji": "✌️", "description": "Scissors face — depicts separation, opposition, and lightning."},
    "Mayura":        {"display": "Mayūra",        "devanagari": "मयूर",         "emoji": "\U0001F99A", "description": "The peacock's beak — used for omens and wiping away tears."},
    "Ardhachandra":  {"display": "Ardhachandra",  "devanagari": "अर्धचन्द्र",   "emoji": "\U0001F313", "description": "Half moon — depicts the moon, a plate, and quiet anxiety."},
    "Arala":         {"display": "Arāla",         "devanagari": "अराल",         "emoji": "\U0001F932", "description": "Bent — used to depict drinking nectar or sipping holy water."},
    "Katamukaha":    {"display": "Kaṭakāmukha",   "devanagari": "कटकामुख",     "emoji": "\U0001F90F", "description": "Link in a chain — used for picking flowers and holding a mirror."},
    "Simhamukaha":   {"display": "Siṁhamukha",    "devanagari": "सिंहमुख",      "emoji": "\U0001F981", "description": "Lion face — depicts the hare, the lotus, deer, and healing."},
    "Kapitha":       {"display": "Kapittha",      "devanagari": "कपित्थ",       "emoji": "\U0001F44C", "description": "Wood apple — used for Lakshmī, Sarasvatī, and holding cymbals."},
    "Mushti":        {"display": "Muṣṭi",         "devanagari": "मुष्टि",        "emoji": "✊",  "description": "The fist — represents grasping objects, wrestling, and steadfastness."},
    "Soochi":        {"display": "Sūchī",         "devanagari": "सूचि",         "emoji": "☝️", "description": "The needle — depicts oneness, the sun, the world, and threading."},
    "Chandrakala":   {"display": "Chandrakalā",   "devanagari": "चन्द्रकला",     "emoji": "\U0001F319", "description": "Crescent moon — used to depict the moon and the face."},
    "Mrigashirsha":  {"display": "Mṛgaśīrṣa",     "devanagari": "मृगशीर्ष",      "emoji": "\U0001F98C", "description": "Deer head — symbolizes the deer, calling, and a graceful woman."},
    "Alapadmakam":   {"display": "Alapadma",      "devanagari": "अलपद्म",       "emoji": "\U0001FAB7", "description": "Lotus in full bloom — depicts beauty, longing, and the lotus flower."},
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/current_mudra')
def current_mudra():
    info = MUDRA_INFO.get(current_mudra_name)
    if info is None:
        return jsonify({"name": None})
    return jsonify({"name": current_mudra_name, **info})


def generate_frames():
    global current_mudra_name
    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        lmList = handLandmarks(imgRGB)

        if len(lmList) != 0:
            x1, y1 = lmList[4][1:]   # Thumb
            x2, y2 = lmList[8][1:]   # Index
            x3, y3 = lmList[12][1:]  # Middle
            x4, y4 = lmList[16][1:]  # Ring
            x5, y5 = lmList[20][1:]  # Pinky
            finger = fingers(lmList)

            draw_fingertip_overlay(img, [(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)])

            lengththind = hypot(x2 - x1, y2 - y1)  # Distance from thumb to index
            lengththindlist.append(lengththind)
            lengthindmid = hypot(x3 - x2, y3 - y2)  # Distance from index to middle
            lengthindmidlist.append(lengthindmid)
            lengthmidrin = hypot(x4 - x3, y4 - y3)  # Distance from Middle to Ring
            lengthmidrinlist.append(lengthmidrin)
            lengthrinpin = hypot(x5 - x4, y5 - y5)  # Distance from Ring to pinky
            lengthrinpinlist.append(lengthrinpin)
            lengthrinthu = hypot(x4 - x1, y4 - y1)  # Distance from Ring to Thumb
            lengthrinthulist.append(lengthrinthu)
            lengthmidthu = hypot(x3-x1,y3-y1)## Distance from Middle to Thumb
            lengthmidthulist.append(lengthmidthu)
            print("Calculation for Thumb to Index")
            print("The average distance",np.mean(lengththindlist))
            print("The Minimum Value",np.min(lengththindlist))
            print("The Maximum Value",np.max(lengththindlist))
            print("Calculation for Index to Middle")
            print("The average distance",np.mean(lengthindmidlist))
            print("The Minimum Value",np.min(lengthindmidlist))
            print("The Maximum Value",np.max(lengthindmidlist))
            print("Calculation for Middle to Ring")
            print("The average distance",np.mean(lengthmidrinlist))
            print("The Minimum Value",np.min(lengthmidrinlist))
            print("The Maximum Value",np.max(lengthmidrinlist))
            print("Calculation for Ring to Pinky")
            print("The average distance",np.mean(lengthrinpinlist))
            print("The Minimum Value",np.min(lengthrinpinlist))
            print("The Maximum Value",np.max(lengthrinpinlist))
            print("Calculation for Ring to Thumb")
            print("The average distance",np.mean(lengthrinthulist))
            print("The Minimum Value",np.min(lengthrinthulist))
            print("The Maximum Value",np.max(lengthrinthulist))

            ##1
            if finger[1] == 1 and finger[0] == 1 and finger[2]==1 and finger[3] == 1 and finger[4]==1 and lengththind<150:
                current_mudra_name = "Pataka"
            ##2
            if finger[1] == 1 and finger[2]==1 and finger[3] == 0 and finger[4]==1 and lengthrinthu>40:
                current_mudra_name = "Tripataka"

            ##3
            if finger[0] == 1 and finger[1] == 0 and finger[2]==0 and finger[3] == 0 and finger[4]==0 :
                current_mudra_name = "Shikaram"
            ##4
            if finger[0] == 0 and finger[1] == 1 and finger[2]==1 and finger[3] == 0 and finger[4]==0 :
                current_mudra_name = "Ardhapataka"
            ##5
            if finger[0] == 0 and finger[1] == 1 and finger[2]==1 and finger[3] == 0 and finger[4]==0 and 19<=lengthindmid<=94  :
                current_mudra_name = "Kartharimukha"

            ##6
            if finger[1] == 1 and finger[2]==1 and finger[3] == 0 and finger[4]== 1 and 12<=lengthrinthu<=40  :
                current_mudra_name = "Mayura"
            ##7
            if finger[1] == 1 and finger[0] == 1 and finger[2]==1 and finger[3] == 1 and finger[4]==1 and 150<=lengththind<=300:
                current_mudra_name = "Ardhachandra"
            ##8
            if finger[1] == 0 and finger[0] == 1 and finger[2]==1 and finger[3] == 1 and finger[4]==1 :
                current_mudra_name = "Arala"
            ##9
            if finger[3] == 1 and finger[4]==1 and 7<=lengthmidthu<= 40 and 5<=lengththind<= 30 and 10<=lengthindmid<=33:
                current_mudra_name = "Katamukaha"
            ##10
            if finger[1] == 1 and finger[4  ]==1 and 3<=lengthrinthu<= 30 and 1<=lengthmidthu<=15 and 1<=lengthmidrin<=25:
                current_mudra_name = "Simhamukaha"
            ##11
            if finger[2] == 0 and finger[3  ]==0 and finger[4] ==0 and finger[0] == 1 and 10<=lengththind<=40:
                current_mudra_name = "Kapitha"
            ##12
            if finger[1] == 0 and finger[0] == 0 and finger[2]==0 and finger[3] == 0 and finger[4]==0 and 3<=lengththind<=15:
                current_mudra_name = "Mushti"
            ##13

            if finger[1] == 1 and finger[0] == 0 and finger[2]==0 and finger[3] == 0 and finger[4]==0:
                current_mudra_name = "Soochi"
            ##14
            if finger[1] == 1 and finger[0] == 1 and finger[2]==0 and finger[3] == 0 and finger[4]==0:
                current_mudra_name = "Chandrakala"
            ##15

            if finger[1] == 0 and finger[0] == 1 and finger[2]==0 and finger[3] == 0 and finger[4]==1:
                current_mudra_name = "Mrigashirsha"
            ##16
            if finger[1] == 1 and finger[0] == 1 and finger[2]==1 and finger[3] == 1 and finger[4]==0 and 30<=lengththind<=155 and 20<=lengthindmid<=70 and 10<=lengthmidrin<=120:
                current_mudra_name = "Alapadmakam"




            cv2.imshow("Webcam", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
