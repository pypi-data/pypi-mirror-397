import subprocess
import time
import pyautogui

pyautogui.FAILSAFE = False

ADB_PATH = "adb"  # Example: r"C:\platform-tools\adb.exe"

__version__ = "0.1.0"


# ================== CORE ==================

def _run(cmd, wait=0):
    """
    Executes an ADB command and returns stdout output.
    """
    result = subprocess.run(
        f'{ADB_PATH} {cmd}',
        shell=True,
        capture_output=True,
        text=True
    )

    if wait > 0:
        time.sleep(wait)

    if result.stderr:
        print("ADB ERROR:", result.stderr.strip())

    return result.stdout.strip()


# ================== CONNECTION ==================

COMMON_PORTS = [
    5554, 5555, 5556, 5557,   # BlueStacks
    62001, 62025,            # Nox
    21503, 21513,            # MeMu
    7555,                    # Genymotion
]


def connect(port=5555, ip="127.0.0.1"):
    """
    Connects to a specific ADB device.
    """
    return _run(f"connect {ip}:{port}")


def disconnect():
    """
    Disconnects all ADB devices.
    """
    return _run("disconnect")


def devices():
    """
    Lists connected ADB devices.
    """
    return _run("devices")


def get_connected_devices():
    """
    Returns a list of connected device IDs.
    """
    out = _run("devices")
    lines = out.splitlines()
    result = []

    for line in lines:
        if "\tdevice" in line:
            result.append(line.split("\t")[0])

    return result


def smart_connect(start_port=5555, end_port=5565, ip="127.0.0.1"):
    """
    Automatically scans ports and connects to the first available device.
    """
    print("🔍 Checking existing ADB connections...")

    devices = get_connected_devices()
    if devices:
        print(f"✅ Already connected: {devices[0]}")
        return devices[0]

    print("⚠️ No devices found, scanning ports...")

    for port in range(start_port, end_port + 1):
        _run(f"connect {ip}:{port}")
        time.sleep(0.4)

        devices = get_connected_devices()
        if devices:
            print(f"🎯 Connected to {devices[0]}")
            return devices[0]

    print("❌ No emulator found")
    return None


def smart_connect_fallback(ip="127.0.0.1"):
    """
    Tries common emulator ports before scanning range.
    """
    for port in COMMON_PORTS:
        _run(f"connect {ip}:{port}")
        time.sleep(0.3)

    return smart_connect(ip=ip)


# ================== KEYS ==================

def home(wait=0):
    """Press HOME key."""
    return _run("shell input keyevent KEYCODE_HOME", wait)


def back(wait=0):
    """Press BACK key."""
    return _run("shell input keyevent KEYCODE_BACK", wait)


def recent(wait=0):
    """Open recent apps."""
    return _run("shell input keyevent KEYCODE_APP_SWITCH", wait)


# ================== TOUCH ==================

def tap(x, y, wait=0):
    """Tap screen at (x, y)."""
    return _run(f"shell input tap {x} {y}", wait)


def swipe(x1, y1, x2, y2, duration=300, wait=0):
    """Swipe from point A to B."""
    return _run(
        f"shell input swipe {x1} {y1} {x2} {y2} {duration}",
        wait
    )


# ================== TEXT ==================

def text(msg, wait=0):
    """
    Inputs text safely into the device.
    """
    safe = msg.replace(" ", "%s")
    return _run(f'shell input text "{safe}"', wait)


# ================== APPS ==================

def open_app(package, wait=0):
    """
    Launch an Android app by package name.
    """
    return _run(
        f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1",
        wait
    )


def close_app(package, wait=0):
    """
    Force-stop an Android app.
    """
    return _run(f"shell am force-stop {package}", wait)


# ================== SCREENSHOT ==================

def screenshot(path="screen.png", wait=0):
    """
    Takes a screenshot using exec-out (fast & clean).
    """
    with open(path, "wb") as f:
        subprocess.run(
            f'{ADB_PATH} exec-out screencap -p',
            shell=True,
            stdout=f
        )

    if wait > 0:
        time.sleep(wait)

    return path


def pull_screenshot(path="screen.png", wait=0):
    """
    Windows-safe screenshot method using screencap + pull.
    """
    remote = "/sdcard/__tmp_screen.png"

    subprocess.run([ADB_PATH, "shell", "screencap", "-p", remote])
    subprocess.run([ADB_PATH, "pull", remote, path])
    subprocess.run([ADB_PATH, "shell", "rm", remote])

    if wait:
        time.sleep(wait)

    return path


def safe_screenshot(path="screen.png", delay=0.3):
    """
    Screenshot with delay (useful after animations).
    """
    time.sleep(delay)
    return screenshot(path)


# ================== ZOOM (EMULATOR KEYS) ==================

def zoom_out(key="S", hold=0.7):
    """Zoom out using emulator hotkey."""
    pyautogui.keyDown(key)
    time.sleep(hold)
    pyautogui.keyUp(key)


def zoom_in(key="B", hold=0.7):
    """Zoom in using emulator hotkey."""
    pyautogui.keyDown(key)
    time.sleep(hold)
    pyautogui.keyUp(key)


def human_zoom_out(key="S"):
    """Human-like zoom out."""
    for t in (0.4, 0.3):
        pyautogui.keyDown(key)
        time.sleep(t)
        pyautogui.keyUp(key)
        time.sleep(0.2)


def human_zoom_in(key="B"):
    """Human-like zoom in."""
    for t in (0.4, 0.3):
        pyautogui.keyDown(key)
        time.sleep(t)
        pyautogui.keyUp(key)
        time.sleep(0.2)
