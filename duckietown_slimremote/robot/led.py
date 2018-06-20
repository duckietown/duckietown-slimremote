# authors: Valerio Varricchio <valerio@mit.edu>
#          Luca Carlone <lcarlone@mit.edu>
#          Dmitry Yershov <dmitry.s.yershov@gmail.com>
#


class RGB_LED():
    OFFSET_RED = 0
    OFFSET_GREEN = 1
    OFFSET_BLUE = 2

    def __init__(self, debug=False):
        from Adafruit_MotorHAT.Adafruit_PWM_Servo_Driver import PWM  # @UnresolvedImport
        self.pwm = PWM(address=0x40, debug=debug)
        for i in range(15):
            self.pwm.setPWM(i, 0, 4095)

    def setLEDBrightness(self, led, offset, brightness):
        self.pwm.setPWM(3 * led + offset, brightness << 4, 4095)

    def setRGBint24(self, led, color):
        r = color >> 16 & 0xFF
        g = color >> 8 & 0xFF
        b = color >> 0 & 0xFF
        self.setRGBvint8(led, [r, g, b])

    def setRGBvint8(self, led, color):
        self.setLEDBrightness(led, self.OFFSET_RED, color[0])
        self.setLEDBrightness(led, self.OFFSET_GREEN, color[1])
        self.setLEDBrightness(led, self.OFFSET_BLUE, color[2])

    def setRGB(self, led, color):
        assert len(color) == 3
        assert min(color) >= 0
        assert max(color) <= 1
        self.setRGBvint8(led, [int(c * 255) for c in color])

    def __del__(self):
        for i in range(15):
            self.pwm.setPWM(i, 0, 4095)
        del self.pwm


TOP = 'top'
BACK_LEFT = 'bl'
BACK_RIGHT = 'br'
FRONT_LEFT = 'fl'
FRONT_RIGHT = 'fr'


class DuckietownLights():
    # Configuration (calibration) - needs to be in a yaml.file
    name2port = {
        TOP: 2,
        BACK_LEFT: 1,
        BACK_RIGHT: 3,
        FRONT_LEFT: 0,
        FRONT_RIGHT: 4,
    }

    # name -> sequence
    sequences = {}

    car_all_lights = [TOP, BACK_LEFT, BACK_RIGHT, FRONT_LEFT, FRONT_RIGHT]