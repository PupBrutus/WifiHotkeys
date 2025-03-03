#Code needs to create an API endpoint so that the pi can be controlled from the web. Commands sent via the API will be executed on the pi sending keyboard commands to the system it's connected to.
import board
import digitalio
import time
import busio
import os
import ipaddress
import wifi
import socketpool
from adafruit_httpserver import Server, Route, as_route, Request, Response, GET, POST
import adafruit_requests as requests

import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Connect to wifi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("My IP address is", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)
print("Listening on http://%s:80" % wifi.radio.ipv4_address)

# Route definitions -
@server.route("/")
def base(request: Request):
    """
    Serve an HTML page with buttons to execute API commands.
    """
    html_content = """
    <html>
    <head>
        <title>Pi Control</title>
    </head>
    <body>
        <h1>Control the Pi</h1>
        <button onclick="sendCommand('/teams?cmd=muteMic')">Mute Mic</button>
        <button onclick="sendCommand('/teams?cmd=videoToggle')">Toggle Video</button>
        <button onclick="sendCommand('/teams?cmd=joinFromOutlook')">Join from Outlook</button>
        <button onclick="sendCommand('/teams?cmd=acceptAudioOnly')">Accept Audio Only</button>
        <button onclick="sendCommand('/teams?cmd=acceptAudioVideo')">Accept Audio/Video</button>
        <button onclick="sendCommand('/teams?cmd=disconnect')">Disconnect</button>
        <button onclick="sendCommand('/message?cmd=string')">Send Message</button>
        <script>
            function sendCommand(url) {
                fetch(url)
                    .then(response => response.text())
                    .then(data => alert(data))
                    .catch(error => alert('Error: ' + error));
            }
        </script>
    </body>
    </html>
    """
    return Response(request, html_content, content_type="text/html")


@server.route("/teams", GET)
def teamsCmds(request: Request):
    cmd = request.query_params.get("cmd")
    try:
        if cmd == "muteMic":
            keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.M) #Toggle mute
            time.sleep(0.1)
        if cmd == "videoToggle":
            keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.O) #Toggle video
            time.sleep(0.1)
        if cmd == "joinFromOutlook":
            keyboard.send(Keycode.ALT, Keycode.SHIFT, Keycode.J) #Join meeting from outlook reminder
            time.sleep(0.1)
        if cmd == "acceptAudioOnly":
            keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.S) #Accept call with audio only
            time.sleep(0.1)
        if cmd == "acceptAudioVideo":
            keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.A) #Accept call with audio/video
            time.sleep(0.1)
        if cmd == "disconnect":
            keyboard.send(Keycode.CONTROL, Keycode.SHIFT, Keycode.H) #Disconnect from call
            time.sleep(0.1)
        time.sleep(0.1)
        return Response(request, f"Sent command: " + cmd)
    except:
        return Response(request, f"Error sending command: " + cmd)
    
@server.route("/message", GET)
def teamsCmds(request: Request):
    cmd = request.query_params.get("cmd")
    try:
        if cmd == "string":
            message = "This is some long string that I want to send to the computer."
            keyboard_layout.write(message)
            time.sleep(0.1)
        time.sleep(0.1)
        return Response(request, f"Sent command: " + cmd)
    except:
        return Response(request, f"Error sending command: " + cmd)

server.serve_forever(str(wifi.radio.ipv4_address))