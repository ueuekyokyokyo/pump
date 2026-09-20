import socket
import ujson


# ==========================
# getリクエストからqueryを取得する queryがなければnullを返す
# ==========================
def get_query(get_request):

    # GET /?startDay=...&action=set HTTP/1.1
    #      ↑　　　　　　　　　　　　　　　　　　　↑を探す
    start = get_request.find("?")

    #　urlの値を解析する ?から始まる位置
    # getできる値がなかったとき
    if start == -1:
        return ""
    start += 1
    end = get_request.find(" ", start)

    if end == -1:
        return ""

    return get_request[start:end]

# ==========================
# queryから値を取得する
# ==========================
def get_query_value(query, key):
    
    # keyに一致したvalueのみ返す

    for item in query.split("&"):

        if "=" not in item:
            continue

        name, value = item.split("=", 1)

        if name == key:
            return value.replace("%3A", ":")

    return ""



# ==========================
# settingsのデータを読み込み
# ==========================

with open("settings.json", "r") as f:
    settings = ujson.load(f)


# ==========================
# index.htmlのデータを読み込み
# ==========================

with open("index.html", "r") as f:
    html = f.read()


# ==========================
# Webサーバー
# ==========================

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

# 接続がなければすぐmain.pyに戻る
s.setblocking(False)

print("Webサーバー起動")


# ==========================



# ==========================
# update
# ==========================

def update():

    try:
        cl, addr = s.accept()

    except OSError:
        return

    print("client connected from", addr)
    
#    cl.settimeout(1)

    try:
        
        cl.settimeout(5)

        # ブラウザからのリクエスト
        request = cl.recv(1024)
        request = request.decode()
        print(request)
        
        query = get_query(request)
        
        if query:
            action = get_query_value(query,"action")

            # ======================
            # 設定を保存
            # ======================

            if action == "set":

                start_day = get_query_value(request, "startDay")
                start_time = get_query_value(request, "startTime")
                interval = get_query_value(request, "howMany")
                duration = get_query_value(request, "howLong")
                check = get_query_value(request, "check")
                

                print("start_day :", repr(start_day))
                print("start_time:", repr(start_time))
                print("interval  :", repr(interval))
                print("duration  :", repr(duration))
                print("check     :", repr(check))


                if start_day:
                    settings["start_day"] = start_day

                if start_time:
                    settings["start_time"] = start_time

                if interval:
                    settings["interval"] = interval
                    
                if duration:
                    settings["duration"] = duration

                settings["check"] = bool(check)
                

                with open("settings.json", "w") as f:
                    ujson.dump(settings, f)


            # ======================
            # 手動ON
            # ======================

            elif action == "pump_on":
                print("manual_on")
                # pump.manual_on()


            # ======================
            # 手動OFF
            # ======================

            elif action == "pump_off":
                print("manual_on")
                # pump.manual_off()



        # ==========================
        # HTMLを返す
        # ==========================

        # ヘッダー部分
        http_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        
        html_contents = html % (
            settings["start_day"],
            settings["start_time"],
            settings["interval"],
            settings["duration"],
            "checked" if settings["check"] else "",
            settings["start_day"],
            settings["start_time"],
            settings["interval"],
            settings["duration"],
            "checked" if settings["check"] else ""

        )
        
        full_response = http_header+html_contents
        
        
        print("HTML作成完了")
        print("設定:", settings)
        print("HTML送信開始")

        cl.send(full_response.encode())
        print("HTML送信完了")
    except Exception as e:

        print("Webエラー:", e)

    finally:
        cl.close()
