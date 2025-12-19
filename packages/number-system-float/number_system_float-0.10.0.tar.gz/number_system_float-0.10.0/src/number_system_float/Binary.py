from math import log2


class bin_float:
    def __init__(self, value):
        if not isinstance(value, float):
            raise TypeError("The class 'bin_float' is built for binary floats.")
        else:
            self.value = value

    def __repr__(self):
        message = "0bf"

        if self.value == 0:
            message += "0"
            return message

        else:
            value = self.value

            N = int(log2(self.value) // 1)

            if N < 0:
                N = 0

            for i in range(N, -10, -1):
                if value >= 2**i:
                    message += "1"
                    value -= 2**i
                else:
                    message += "0"
                if i == 0:
                    message += "."

            message = message.strip("0")
            return message

    def __str__(self):
        message = "0bf"


        if self.value == 0:
            message += "0"
            return message

        else:
            value = self.value

            N = int(log2(self.value) // 1)

            if N < 0:
                N = 0

            for i in range(N, -10, -1):
                if value >= 2**i:
                    message += "1"
                    value -= 2**i
                else:
                    message += "0"
                if i == 0:
                    message += "."

            message = message.strip("0")
            return message

    def __add__(self, other):
        return bin_float(self.value + other.value)

    def __sub__(self, other):
        return bin_float(self.value + other.value)

    def __mul__(self, other):
        return bin_float(self.value * other.value)

    def __truediv__(self, other):
        return bin_float(self.value / other.value)

    def __floordiv__(self, other):
        return bin_float(self.value // other.value)

    def __mod__(self, other):
        return bin_float(self.value % other.value)

    def __round__(self):
        return bin(int(round(self.value)))

    def __float__(self):
        return self.value