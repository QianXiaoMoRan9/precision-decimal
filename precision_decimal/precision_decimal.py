"""
Integer representation of float to try to overcome float limitations
"""

class PrecisionDecimal(object):
    """
    Number of nums after the decimal point we want to get to, no matter the value
    12.34 -> precision is 2
    1.0000 -> precision is 4
    Integer value could have precisions as defined by the user or default to 2
    """
    precision: int
    """
    The integer value we use to represent the float in integer form that accounts for precision
    This will always be a value that has abs value >= 1
    value 1234, precision 2 -> 12.34
    value 10000, precision 1 -> 1000.0
    """
    value: int

    def __init__(self, value: int, precision: int):
        assert type(value) == int, "Value should be an integer"
        self._check_precision(precision)
        self.precision = precision
        self.value = value

    @staticmethod
    def from_int(value: int, precision: int = 2) -> 'PrecisionDecimal':
        res = PrecisionDecimal(0, precision)
        res.value = value
        return res

    @staticmethod
    def from_string(s: str, precision:None or int = None) -> 'PrecisionDecimal':
        # Get the int part
        number_split = s.split(".")
        assert 0 < len(number_split) < 3, "Invalid format of a decimal"
        # Infer the precision from number in the string
        if precision is None:
            # if this is an int, then default to 2
            if len(number_split) == 1:
                precision = 2
                number_split.append("00")
            else:
                precision = len(number_split[1])
        else:
            if len(number_split) == 2:
                # trim excess numbers after decimal point
                if len(number_split[1]) > precision:
                    number_split[1] = number_split[1][: precision]
                elif len(number_split[1]) < precision:
                    number_split[1] = number_split[1] + ("0" * (precision - len(number_split[1])))
        int_number = int("".join(number_split))
        return PrecisionDecimal(int_number, precision)

    @staticmethod
    def from_float(num: float, precision: int) -> 'PrecisionDecimal':
        return PrecisionDecimal(int(num * 10 ** precision), precision)

    def to_float(self) -> float:
        return self.value * 10**(-self.precision)

    def change_precision(self, new_precision: int) -> 'PrecisionDecimal':
        if new_precision >= self.precision:
            return PrecisionDecimal.from_int(self.value * 10 ** (new_precision - self.precision), new_precision)
        else:
            return PrecisionDecimal.from_int(self.value // 10 ** (self.precision - new_precision), new_precision)

    def __add__(self, other):
        other = self._convert_type(other)
        return PrecisionDecimal.from_int(self.value + other.value, self.precision)

    def __sub__(self, other):
        other = self._convert_type(other)
        return PrecisionDecimal.from_int(self.value - other.value, self.precision)

    def __mul__(self, other):
        other = self._convert_type(other)
        res = PrecisionDecimal.from_int(self.value * other.value, self.precision + other.precision)
        return res.change_precision(self.precision)

    def __truediv__(self, other):
        other = self._convert_type(other)
        result_value = 0
        dividend = abs(self.value)
        divisor = abs(other.value)

        for exponent in range(0, self.precision + 1):
            result_value += dividend // divisor
            result_value *= 10
            dividend = dividend % divisor * 10

        if (self.value < 0 and other.value > 0) or (self.value > 0 and other.value < 0):
            result_value = -result_value
        return PrecisionDecimal(result_value, self.precision)

    def __invert__(self):
        return PrecisionDecimal.from_int(-self.value, self.precision)

    def __repr__(self):
        cur_precision = self.precision
        cur_value = abs(self.value)
        res_list = []
        while(cur_precision > 0):
            res_list.insert(0, str(cur_value % 10))
            cur_value //= 10
            cur_precision -= 1
        res_list.insert(0, '.')
        res_list.insert(0, int(cur_value))
        if (self.value < 0):
            res_list.insert(0, '-')
        return f"PrecisionDecimal({''.join(res_list)})"

    def __eq__(self, other):
        if type(other) != PrecisionDecimal:
            return False
        return self.value == other.value and self.precision == other.precision

    def __gt__(self, other):
        other = self._convert_type(other)
        return self.value > other.value

    def __ge__(self, other):
        other = self._convert_type(other)
        return self.value >= other.value

    def __lt__(self, other):
        other = self._convert_type(other)
        return self.value < other.value

    def __le__(self, other):
        other = self._convert_type(other)
        return self.value <= other.value

    def __hash__(self):
        return hash((self.value, self.precision))

    def _check_precision(self, precision):
        assert precision >= 0, "Precision should be non-negative"
        assert type(precision) == int, "Precision value should be of type int"

    def _convert_type(self, other) -> 'PrecisionDecimal':
        if type(other) != PrecisionDecimal:
            if type(other) == float:
                other = self.from_float(other, self.precision)
            elif type(other) == int:
                other = self.from_int(other, self.precision)
            else:
                raise Exception("Unsupported type operation: ", type(other))
        else:
            assert self.precision == other.precision, f"Precision should be the same, this {self.precision}, other: {other.precision}"
        return other
