from math import log


class oct_float:
    def __init__(self, value):
        if not isinstance(value, float):
            raise TypeError("The class 'oct_float' is built for octal floats.")
        else:
            self.value = value

    def __repr__(self):
        message = "0of"

        N = int(log(self.value) // log(8))
        value = self.value

        if N < 0:
            N = 0

        for i in range(N, -10, -1):
            if value // 8**i == 1:
                message += "1"
                value -= 8**i
            elif value // 8**i == 2:
                message += "2"
                value -= 2 * 8**i
            elif value // 8**i == 3:
                message += "3"
                value -= 3 * 8**i
            elif value // 8**i == 4:
                message += "4"
                value -= 4 * 8**i
            elif value // 8**i == 5:
                message += "5"
                value -= 5 * 8**i
            elif value // 8**i == 6:
                message += "6"
                value -= 6 * 8**i
            elif value // 8**i == 7:
                message += "7"
                value -= 7 * 8**i
            else:
                message += "0"
            if i == 0:
                message += "."

        message = message.strip("0")
        return message

    def __str__(self):
        message = "0of"

        N = int(log(self.value) // log(8))
        value = self.value

        if N < 0:
            N = 0

        for i in range(N, -10, -1):
            if value // 8**i == 1:
                message += "1"
                value -= 8**i
            elif value // 8**i == 2:
                message += "2"
                value -= 2 * 8**i
            elif value // 8**i == 3:
                message += "3"
                value -= 3 * 8**i
            elif value // 8**i == 4:
                message += "4"
                value -= 4 * 8**i
            elif value // 8**i == 5:
                message += "5"
                value -= 5 * 8**i
            elif value // 8**i == 6:
                message += "6"
                value -= 6 * 8**i
            elif value // 8**i == 7:
                message += "7"
                value -= 7 * 8**i
            else:
                message += "0"
            if i == 0:
                message += "."

        message = message.strip("0")
        return message
    
    def __add__(self, other):
        return oct_float(self.value + other.value)

    def __sub__(self, other):
        return oct_float(self.value + other.value)

    def __mul__(self, other):
        return oct_float(self.value * other.value)

    def __truediv__(self, other):
        return oct_float(self.value / other.value)

    def __floordiv__(self, other):
        return oct_float(self.value // other.value)

    def __mod__(self, other):
        return oct_float(self.value % other.value)

    def __round__(self):
        return bin(int(round(self.value)))

    def __float__(self):
        return self.value