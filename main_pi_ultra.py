import time
import RPi.GPIO as GPIO
import automation_pre_test
import base_motors

# ================= AUTO CONTROL FLAG =================
AUTO_MODE_ACTIVE = True

# --- PIN CONFIGURATION ---
GPIO_TRIGGER = 8
GPIO_ECHO = 7

# --- SETTINGS ---
TARGET_MIN = 10
TARGET_MAX = 15
FAR_LIMIT = 70
STABILITY_TIME = 2.0

# --- SETUP GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def get_distance():
    GPIO.output(GPIO_TRIGGER, False)
    time.sleep(0.00001)

    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    start_time = time.time()
    stop_time = time.time()
    timeout = time.time() + 0.1

    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return -1

    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return -1

    elapsed = stop_time - start_time
    distance = (elapsed * 34300) / 2
    return distance

def main():
    global AUTO_MODE_ACTIVE

    print("Automatic Mode Started")

    far_start_time = None

    try:
        while AUTO_MODE_ACTIVE:

            dist = get_distance()

            if dist == -1:
                continue

            print(f"Distance: {dist:.1f} cm")

            if dist < TARGET_MIN:
                base_motors.backward()
                far_start_time = None

            elif TARGET_MIN <= dist <= TARGET_MAX:
                base_motors.stop()
                automation_pre_test.automation_sequence()
                time.sleep(2)
                far_start_time = None

            elif TARGET_MAX < dist < FAR_LIMIT:

                if far_start_time is None:
                    far_start_time = time.time()
                    base_motors.stop()

                elapsed = time.time() - far_start_time

                if elapsed >= STABILITY_TIME:
                    base_motors.forward()
                else:
                    base_motors.stop()

            else:
                base_motors.stop()
                far_start_time = None

            time.sleep(0.1)

    except Exception as e:
        print("Auto Error:", e)

    base_motors.stop()
    print("Automatic Mode Stopped")

def stop_auto():
    global AUTO_MODE_ACTIVE
    AUTO_MODE_ACTIVE = False
