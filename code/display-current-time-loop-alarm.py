import time, os
from tm1637 import TM1637

display = TM1637(CLK=21, DIO=20)
display.showColon(True)

alarmTimeHr = 22
alarmTimeMin = 26

while True:
    try:
        currentTime = time.localtime()
        hrDigit1 = currentTime.tm_hour // 10
        hrDigit2 = currentTime.tm_hour % 10
        minDigit1 = currentTime.tm_min // 10
        minDigit2 = currentTime.tm_min % 10
        digits = [hrDigit1, hrDigit2, minDigit1, minDigit2]
        display.show(digits)
        print(digits)
        
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


