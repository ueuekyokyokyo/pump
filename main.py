import time
import network
import ntptime
from machine import Pin, RTC
from secret import ssid, password

import control

# ==========================
# モーター制御
# ==========================
motor = Pin(22, Pin.OUT)
motor.off()

# ==========================
# オンボードLED
# ==========================
led = Pin("LED", Pin.OUT)
led.off()



# ==========================
# Wi-Fi接続
# ==========================
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Wi-Fi接続中...")

while not wlan.isconnected():
    time.sleep(1)

print("Wi-Fi接続完了")
print("IPアドレス:", wlan.ifconfig()[0])

# ==========================
# RTC
# ==========================
rtc = RTC()

# ==========================
# NTP同期
# ==========================
try:

    print("NTPから時刻取得中...")

    ntptime.host = "time.google.com"
    ntptime.settime()

    utc = time.localtime(time.time() + 9 * 3600)

    rtc.datetime((
        utc[0],
        utc[1],
        utc[2],
        utc[6],
        utc[3],
        utc[4],
        utc[5],
        0
    ))

    print("NTP同期成功")
    
    for _ in range(3):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

except Exception as e:

    print("NTP同期失敗:", e)
    print("手動時刻を使用します")
    
    # 失敗を知らせる
    led.on()
    time.sleep(2)
    led.off()

    rtc.datetime((
        2026,
        7,
        30,
        0,
        12,
        0,
        0,
        0
    ))

print("現在時刻:", rtc.datetime())



# ==========================
# メインループ
# ==========================
while True:

    control.update()


    # # 現在時刻（JST）
    # current_epoch = int(time.time())

    # now = time.localtime(current_epoch)

    # print(
    #     f"{now[0]}/{now[1]:02}/{now[2]:02} "
    #     f"{now[3]:02}:{now[4]:02}:{now[5]:02}"
    # )

    # if current_epoch >= target_epoch:

    #     run_count += 1

    #     print(f"\n===== {run_count}回目 =====")

    #     motor.on()

    #     time.sleep(RUN_TIME)

    #     motor.off()


    #     # 現在時刻を取り直す
    #     current_epoch = int(time.time() + 9 * 3600)

    #     while target_epoch <= current_epoch:
    #         target_epoch += INTERVAL


    # # 2回実行したら終了
    # if run_count >= 2:
    #     print("2回実行したので終了します。")
    #     break


    time.sleep(1)
