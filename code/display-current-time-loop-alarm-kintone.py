import time, os, sys, kintone
from tm1637 import TM1637

#sdomain = "SUB-DOMAIN-NAME"
#appId = "APP-ID-NUMBER"
#token = "APP-TOKEN"

sdomain = "jxsboston"
appId = "11"
token = "jQ8NQHzpMGMQoxdbve2frDAlDj18x0oXL61zfqKT"

display = TM1637(CLK=21, DIO=20)
display.showColon(True)

while True:
    try:
        record = kintone.getRecord(subDomain=sdomain,
                                   apiToken=token,
                                   appId=appId,
                                   recordId="1")
        alarmTimeHr = int(record["alarmTimeHr"]["value"])
        alarmTimeMin = int(record["alarmTimeMin"]["value"])
        print("Alarm time: " + str(alarmTimeHr) + ":" + str(alarmTimeMin))

        currentTime = time.localtime()
        hrDigit1 = currentTime.tm_hour // 10
        hrDigit2 = currentTime.tm_hour % 10
        minDigit1 = currentTime.tm_min // 10
        minDigit2 = currentTime.tm_min % 10
        digits = [hrDigit1, hrDigit2, minDigit1, minDigit2]
        display.show(digits)
        print("Clock time updated: " + str(digits))
        
        if(alarmTimeHr == currentTime.tm_hour and
           alarmTimeMin == currentTime.tm_min):
            command = "vlc -I dummy 'http://translate.google.com/translate_tts?"\
                      + "ie=UTF-8&client=tw-ob&tl=ja&"\
                      + "q=ただいま" + str(alarmTimeHr % 12) + "時"\
                      + str(alarmTimeMin) + "分" + "です' --play-and-exit"
            for i in range(3):
                os.system(command)
                time.sleep(2)
        
        time.sleep(60)        
    except KeyboardInterrupt:
        break

display.cleanup()