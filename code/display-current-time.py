import time
from tm1637 import TM1637

display = TM1637(CLK=21, DIO=20)
display.showColon(True)

currentTime = time.localtime()
hr = currentTime.tm_hour
min = currentTime.tm_min

hrMinStr = str(hr) + str(min)

display.show4digitInt( int(hrMinStr) )
print(hrMinStr)
time.sleep(5)
        
display.cleanup()


