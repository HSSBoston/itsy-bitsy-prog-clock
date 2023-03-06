import time
from tm1637 import TM1637

display = TM1637(CLK=21, DIO=20)
display.showColon(True)

currentTime = time.localtime()
hour = currentTime.tm_hour
if hour == 12:
    hour = 12
else:
    hour = hour % 12

hrDigit1 = hour // 10
hrDigit2 = hour % 10
minDigit1 = currentTime.tm_min // 10
minDigit2 = currentTime.tm_min % 10
digits = [hrDigit1, hrDigit2, minDigit1, minDigit2]

display.show(digits)
print(digits)
time.sleep(5)
        
display.cleanup()


