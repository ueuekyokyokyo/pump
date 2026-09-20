import time
import network
import socket
import ntptime
import time
from machine import Pin
from secret import ssid, password
from html import html
from functions import url_decode, get_query_value


led = Pin("LED", Pin.OUT)
ledState = 'LED State Unknown'


#password = 'jcnwyxrm'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)



# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
# webサーバーとして機能させる
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
s.bind(addr)
s.listen(1)
print('listening on', addr)


try:
    ntptime.settime()
except:
    print("NTP time sync failed")


# Listen for connections, serve client
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)

        request = cl.recv(1024)
        print(request)
        request = str(request)

        if request.find('led=on') >= 0:
            print("led on")
            led.value(1)

        if request.find('led=off') >= 0:
            print("led off")
            led.value(0)

        ledState = "LED is OFF" if led.value() == 0 else "LED is ON"

        # UTC + 9時間で日本時間
        now = time.time()
        t = time.localtime(now)

        current_time = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )



        message = get_query_value(request, 'message')
        #メッセージを取得できた場合
        if message:
            with open('message.txt', 'w') as f:
                f.write(message)
        #そうでない場合の挙動
        try:
            with open('message.txt', 'r') as f:
                saved_message = f.read()
        except:
            saved_message = ''


        response = html % (saved_message,ledState, current_time)
        full_response = 'HTTP/1.0 200 OK\r\nContent-type: text/html;charset=UTF-8\r\n\r\n' + response

        cl.send(full_response)
        cl.close()

    except OSError as e:
        try:
            cl.close()
        except:
            pass
        print('connection closed')

