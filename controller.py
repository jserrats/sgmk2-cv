import time
from inputs import get_gamepad
import threading
from sgmk2 import SGMk2


def send_updatesX():
    while True:
        if stick_x not in range(-4, 4):
            # print("updating X ", stick_x)
            sgmk2.pan_rel(3 * stick_x)
        time.sleep(0.1)


def send_updatesY():
    while True:
        if stick_y not in range(-3, 3):
            # print("updating Y ", stick_x)
            sgmk2.tilt_rel(stick_y)
        time.sleep(0.1)


def controller():
    global sgmk2
    sgmk2 = SGMk2()
    
    rof_values = [60, 200, 400]
    last_rof = 0
    sgmk2.set_rof(rof_values[last_rof])

    global stick_x
    global stick_y

    stick_x, stick_y = 0, 0

    threading.Thread(target=send_updatesX).start()
    threading.Thread(target=send_updatesY).start()

    sgmk2.toggle_laser()

    while 1:
        events = get_gamepad()

        for event in events:
            # print(event.code, event.state)
            if event.code == "ABS_Z":
                if event.state == 1023:
                    sgmk2.flywheel(True)
                elif event.state == 0:
                    sgmk2.flywheel(False)
            if event.code == "ABS_RZ":
                if event.state == 1023:
                    # print("shooting")
                    sgmk2.shooting(True)
                elif event.state == 0:
                    sgmk2.shooting(False)
            if event.code == "ABS_X":
                stick_x = event.state // (-1 * 1024)
            if event.code == "ABS_Y":
                stick_y = event.state // (-1 * 1024)
            if event.code == "ABS_HAT0Y":
                sgmk2.tilt_rel(-1 * event.state)
            if event.code == "ABS_HAT0X":
                sgmk2.pan_rel(-1 * event.state)
            if event.code == "BTN_TL" and event.state == 1:
                sgmk2.toggle_laser()
            if event.code == "BTN_TR" and event.state == 1:
                last_rof = (last_rof + 1) % 3
                sgmk2.set_rof(rof_values[last_rof])


if __name__ == "__main__":
    controller()
