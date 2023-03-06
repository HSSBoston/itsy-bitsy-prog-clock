import math, threading
import RPi.GPIO as IO
from time import sleep, localtime
# from tqdm import tqdm

# IO.setwarnings(False)
IO.setmode(IO.BCM)

HexDigits = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 
            0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71, 0x3D, 0x76, 
            0x06, 0x1E, 0x76, 0x38, 0x55, 0x54, 0x3F, 0x73, 0x67, 
            0x50, 0x6D, 0x78, 0x3E, 0x1C, 0x2A, 0x76, 0x6E, 0x5B,
            0x00, 0x40, 0x63, 0xFF]

ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0
# DEBUG = False


class TM1637:
    __doublePoint = False
    __Clkpin = 0
    __Datapin = 0
    __brightness = 1.0  # default to max brightness
    __currentData = [0, 0, 0, 0]

    def __init__(self, CLK, DIO, brightness=1.0):
        self.__Clkpin = CLK
        self.__Datapin = DIO
        self.__brightness = brightness
        IO.setup(self.__Clkpin, IO.OUT)
        IO.setup(self.__Datapin, IO.OUT)

    def cleanup(self):
        self.Clear()
        IO.cleanup()        

    def cleanupClock(self):
        """Stop updating clock, turn off display, and cleanup GPIO"""
        self.StopClock()
        self.Clear()
        IO.cleanup()

    def Clear(self):
        b = self.__brightness
        point = self.__doublePoint
        self.__brightness = 0
        self.__doublePoint = False
        data = [0x7F, 0x7F, 0x7F, 0x7F]
        self.show(data)
        # Restore previous settings:
        self.__brightness = b
        self.__doublePoint = point

    def show4digitInt(self, i):
        s = str(i)
        self.Clear()
        for i in range(0, len(s)):
            self.Show1(i, int(s[i]))

    def show(self, data):
        for i in range(0, 4):
            self.__currentData[i] = data[i]

        self.start()
        self.writeByte(ADDR_AUTO)
        self.br()
        self.writeByte(STARTADDR)
        for i in range(0, 4):
            self.writeByte(self.coding(data[i]))
        self.br()
        self.writeByte(0x88 + int(self.__brightness))
        self.stop()

    def Show1(self, DigitNumber, data):
        """show one Digit (number 0...3)"""
        if(DigitNumber < 0 or DigitNumber > 3):
            return  # error

        self.__currentData[DigitNumber] = data

        self.start()
        self.writeByte(ADDR_FIXED)
        self.br()
        self.writeByte(STARTADDR | DigitNumber)
        self.writeByte(self.coding(data))
        self.br()
        self.writeByte(0x88 + int(self.__brightness))
        self.stop()
    # Scrolls any integer n (can be more than 4 digits) from right to left display.
    def ShowScroll(self, n):
        n_str = str(n)
        k = len(n_str)

        for i in range(0, k + 4):
            if (i < k):
                self.show([int(n_str[i-3]) if i-3 >= 0 else None, int(n_str[i-2]) if i-2 >= 0 else None, int(n_str[i-1]) if i-1 >= 0 else None, int(n_str[i]) if i >= 0 else None])
            elif (i >= k):
                self.show([int(n_str[i-3]) if (i-3 < k and i-3 >= 0) else None, int(n_str[i-2]) if (i-2 < k and i-2 >= 0) else None, int(n_str[i-1]) if (i-1 < k and i-1 >= 0) else None, None])
            sleep(1)

    def SetBrightness(self, percent):
        """Accepts percent brightness from 0 - 1"""
        max_brightness = 7.0
        brightness = math.ceil(max_brightness * percent)
        if (brightness < 0):
            brightness = 0
        if(self.__brightness != brightness):
            self.__brightness = brightness
            self.show(self.__currentData)

    def showColon(self, on):
        """Show or hide double point divider"""
        if(self.__doublePoint != on):
            self.__doublePoint = on
            self.show(self.__currentData)

    def writeByte(self, data):
        for i in range(0, 8):
            IO.output(self.__Clkpin, IO.LOW)
            if(data & 0x01):
                IO.output(self.__Datapin, IO.HIGH)
            else:
                IO.output(self.__Datapin, IO.LOW)
            data = data >> 1
            IO.output(self.__Clkpin, IO.HIGH)

        # wait for ACK
        IO.output(self.__Clkpin, IO.LOW)
        IO.output(self.__Datapin, IO.HIGH)
        IO.output(self.__Clkpin, IO.HIGH)
        IO.setup(self.__Datapin, IO.IN)

        while(IO.input(self.__Datapin)):
            sleep(0.001)
            if(IO.input(self.__Datapin)):
                IO.setup(self.__Datapin, IO.OUT)
                IO.output(self.__Datapin, IO.LOW)
                IO.setup(self.__Datapin, IO.IN)
        IO.setup(self.__Datapin, IO.OUT)

    def start(self):
        """send start signal to TM1637"""
        IO.output(self.__Clkpin, IO.HIGH)
        IO.output(self.__Datapin, IO.HIGH)
        IO.output(self.__Datapin, IO.LOW)
        IO.output(self.__Clkpin, IO.LOW)

    def stop(self):
        IO.output(self.__Clkpin, IO.LOW)
        IO.output(self.__Datapin, IO.LOW)
        IO.output(self.__Clkpin, IO.HIGH)
        IO.output(self.__Datapin, IO.HIGH)

    def br(self):
        """terse break"""
        self.stop()
        self.start()

    def coding(self, data):
        if(self.__doublePoint):
            pointData = 0x80
        else:
            pointData = 0

        if(data == 0x7F or data is None):
            data = 0
        else:
            data = HexDigits[data] + pointData
        return data

    def clock(self, military_time):
        """Clock script modified from:
            https://github.com/johnlr/raspberrypi-tm1637"""
        self.showColon(True)
        while (not self.__stop_event.is_set()):
            t = localtime()
            hour = t.tm_hour
            if not military_time:
                hour = 12 if (t.tm_hour % 12) == 0 else t.tm_hour % 12
            d0 = hour // 10 if hour // 10 else 36
            d1 = hour % 10
            d2 = t.tm_min // 10
            d3 = t.tm_min % 10
            digits = [d0, d1, d2, d3]
            self.show(digits)
            # # Optional visual feedback of running alarm:
            # print digits
            # for i in tqdm(range(60 - t.tm_sec)):
            for i in range(60 - t.tm_sec):
                if (not self.__stop_event.is_set()):
                    sleep(1)

    def StartClock(self, military_time=True):
        # Stop event based on: http://stackoverflow.com/a/6524542/3219667
        self.__stop_event = threading.Event()
        self.__clock_thread = threading.Thread(
            target=self.clock, args=(military_time,))
        self.__clock_thread.start()

    def StopClock(self):
        try:
            print ('Attempting to stop live clock')
            self.__stop_event.set()
        except:
            print ('No clock to close')


if __name__ == "__main__":
    """Confirm the display operation"""
    display = TM1637(CLK=21, DIO=20, brightness=1.0)

    display.Clear()

    digits = [1, 2, 3, 4]
    display.show(digits)
    scrap = input("1234  - Working? (Press Key)")

    print ("Updating one digit at a time:")
    display.Clear()
    display.Show1(1, 3)
    sleep(0.5)
    display.Show1(2, 2)
    sleep(0.5)
    display.Show1(3, 1)
    sleep(0.5)
    display.Show1(0, 4)
    scrap = input("4321  - (Press Key)")

    print ("Add double point\n")
    display.showColon(True)
    sleep(0.2)
    print ("Brightness Off")
    display.SetBrightness(0)
    sleep(0.5)
    print ("Full Brightness")
    display.SetBrightness(1)
    sleep(0.5)
    print ("30% Brightness")
    display.SetBrightness(0.3)
    sleep(0.3)
    
    display.cleanup()
