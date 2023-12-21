from flask import Flask, render_template, Response
import cv2
from paho.mqtt import client as mqtt_client
from numpy import sign
from sgmk2 import SGMk2
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")  #
font = cv2.FONT_HERSHEY_SIMPLEX

sgmk2 = SGMk2()

gamepad_axis_cache = [0, 0]
gamepad_buttons_cache = [0 for i in range(17)]


def gen_frames():
    camera = cv2.VideoCapture("http://sgmk2-cam.iot:8080/")  #
    while 1:
        success, img = camera.read()
        if not success:
            print("Camera Offline")
            break
        else:
            # convert to gray scale of each frames
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if sgmk2.autoaim:
                color = (0, 0, 255)  # red
            else:
                color = (0, 255, 0)  # green
            # Detects faces of different sizes in the input image
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            (image_height, image_width) = img.shape[:2]
            image_center = image_center = (image_width // 2, image_height // 2)
            center_x = image_center[0]
            center_y = image_center[1]
            cv2.circle(img, image_center, 7, (0, 0, 255), -1)
            cv2.putText(
                img,
                f"AIMBOT: {sgmk2.autoaim}",
                (10, 450),
                font,
                1,
                color,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                f"ROF: {sgmk2.get_rof_value()}",
                (400, 450),
                font,
                1,
                color,
                2,
                cv2.LINE_AA,
            )
            for x, y, w, h in faces:
                # Aiming inside face
                if (
                    center_x > x
                    and center_x < (x + w)
                    and center_y > y
                    and center_y < y + h
                ):
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.line(
                        img,
                        image_center,
                        ((x + (w // 2)), y + (h // 2)),
                        (0, 0, 255),
                        5,
                    )
                    x_distance = sign(center_x - (x + (w // 2)))
                    y_distance = sign(center_y - (y + (h // 2)))

                else:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    cv2.line(
                        img,
                        image_center,
                        ((x + (w // 2)), y + (h // 2)),
                        (0, 255, 0),
                        5,
                    )

                    x_distance = (center_x - (x + (w // 2))) * 0.1
                    y_distance = (center_y - (y + (h // 2))) * 0.1

                if sgmk2.autoaim:
                    sgmk2.pan_rel(str(x_distance))
                    sgmk2.tilt_rel(str(y_distance))
            # Display an image in a window
            ret, buffer = cv2.imencode(".jpg", img)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )  # concat frame one by one and show result

        # Wait for Esc key to stop
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
    """Video streaming home page."""
    return render_template("index.html")


@socketio.on("axis")
def axis(json):
    data = json["data"]
    x_axis, y_axis = data
    if x_axis < 0.15 and x_axis > -0.15:  # removing stick drift
        x_axis = 0
    x_axis, y_axis = int(x_axis * -20), int(y_axis * -7)

    if x_axis != 0 or gamepad_axis_cache[0] != 0:
        sgmk2.pan_rel(x_axis)
    if y_axis != 0:
        sgmk2.tilt_rel(y_axis)

    gamepad_axis_cache[0], gamepad_axis_cache[1] = x_axis, y_axis
    # print(x_axis, y_axis)


@socketio.on("buttons")
def buttons(json):
    data = json["data"]
    for button, state in enumerate(data):
        if gamepad_buttons_cache[button] != state:
            control(button, state)
            gamepad_buttons_cache[button] = state
            # print(button, state)


def control(button, state):
    if button == 6:
        sgmk2.flywheel(state == 1)
    if button == 7:
        sgmk2.shooting(state == 1)
    if button == 4 and state == 1:
        sgmk2.toggle_laser()
    if button == 5 and state == 1:
        sgmk2.switch_rof()
    if button == 14 and state == 1:
        sgmk2.pan_rel(1)
    if button == 15 and state == 1:
        sgmk2.pan_rel(-1)
    if button == 12 and state == 1:
        sgmk2.tilt_rel(1)
    if button == 13 and state == 1:
        sgmk2.tilt_rel(-1)
    if button == 0 and state == 1:
        sgmk2.autoaim = not sgmk2.autoaim
        if sgmk2.autoaim:
            sgmk2.alert()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True) # enabled because it simplifies concurrency and will not be exposed over internet
