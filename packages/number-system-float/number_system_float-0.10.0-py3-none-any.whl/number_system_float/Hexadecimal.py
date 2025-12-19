from math import log


class hex_float:
    def __init__(self, value):
        if not isinstance(value, float):
            raise TypeError("The class 'hex_float' is built for hexadecimal floats.")
        else:
            self.value = value

    def __repr__(self):
        message = "0xf"

        N = int(log(self.value) // log(16))
        value = self.value

        if N < 0:
            N = 0

        for i in range(N, -10, -1):
            if value // 16**i == 1:
                message += "1"
                value -= 16**i
            elif value // 16**i == 2:
                message += "2"
                value -= 2 * 16**i
            elif value // 16**i == 3:
                message += "3"
                value -= 3 * 16**i
            elif value // 16**i == 4:
                message += "4"
                value -= 4 * 16**i
            elif value // 16**i == 5:
                message += "5"
                value -= 5 * 16**i
            elif value // 16**i == 6:
                message += "6"
                value -= 6 * 16**i
            elif value // 16**i == 7:
                message += "7"
                value -= 7 * 16**i
            elif value // 16**i == 8:
                message += "8"
                value -= 8 * 16**i
            elif value // 16**i == 9:
                message += "9"
                value -= 9 * 16**i
            elif value // 16**i == 10:
                message += "a"
                value -= 10 * 16**i
            elif value // 16**i == 11:
                message += "b"
                value -= 11 * 16**i
            elif value // 16**i == 12:
                message += "c"
                value -= 12 * 16**i
            elif value // 16**i == 13:
                message += "d"
                value -= 13 * 16**i
            elif value // 16**i == 14:
                message += "e"
                value -= 14 * 16**i
            elif value // 16**i == 15:
                message += "f"
                value -= 15 * 16**i
            else:
                message += "0"
            if i == 0:
                message += "."

        message = message.strip("0")
        return message

    def __str__(self):
        message = "0xf"

        N = int(log(self.value) // log(16))
        value = self.value

        if N < 0:
            N = 0

        for i in range(N, -10, -1):
            if value // 16**i == 1:
                message += "1"
                value -= 16**i
            elif value // 16**i == 2:
                message += "2"
                value -= 2 * 16**i
            elif value // 16**i == 3:
                message += "3"
                value -= 3 * 16**i
            elif value // 16**i == 4:
                message += "4"
                value -= 4 * 16**i
            elif value // 16**i == 5:
                message += "5"
                value -= 5 * 16**i
            elif value // 16**i == 6:
                message += "6"
                value -= 6 * 16**i
            elif value // 16**i == 7:
                message += "7"
                value -= 7 * 16**i
            elif value // 16**i == 8:
                message += "8"
                value -= 8 * 16**i
            elif value // 16**i == 9:
                message += "9"
                value -= 9 * 16**i
            elif value // 16**i == 10:
                message += "a"
                value -= 10 * 16**i
            elif value // 16**i == 11:
                message += "b"
                value -= 11 * 16**i
            elif value // 16**i == 12:
                message += "c"
                value -= 12 * 16**i
            elif value // 16**i == 13:
                message += "d"
                value -= 13 * 16**i
            elif value // 16**i == 14:
                message += "e"
                value -= 14 * 16**i
            elif value // 16**i == 15:
                message += "f"
                value -= 15 * 16**i
            else:
                message += "0"
            if i == 0:
                message += "."

        message = message.strip("0")
        return message
    
    def __add__(self, other):
        return hex_float(self.value + other.value)

    def __sub__(self, other):
        return hex_float(self.value + other.value)

    def __mul__(self, other):
        return hex_float(self.value * other.value)

    def __truediv__(self, other):
        return hex_float(self.value / other.value)

    def __floordiv__(self, other):
        return hex_float(self.value // other.value)

    def __mod__(self, other):
        return hex_float(self.value % other.value)

    def __round__(self):
        return bin(int(round(self.value)))

    def __float__(self):
        return self.value