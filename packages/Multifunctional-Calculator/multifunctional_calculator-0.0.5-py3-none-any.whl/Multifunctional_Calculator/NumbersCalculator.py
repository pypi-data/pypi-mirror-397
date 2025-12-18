from decimal import *


class NumbersCalculator:
    def __init__(self):
        pass

    def addition(self, *addends):
        self.__init__()
        Sum = Decimal("0")
        t = int

        if type(addends[0]) is list:
            addends = addends[0]
        for addend in addends:
            Sum += Decimal(f"{addend}")
            if type(addend) is float:
                t = float

        return t(Sum)

    def subtraction(self, minuend, *subtrahends):
        self.__init__()
        difference = Decimal(f"{minuend}")
        t = int

        if type(subtrahends[0]) is list:
            subtrahends = subtrahends[0]
        for subtrahend in subtrahends:
            difference -= Decimal(f"{subtrahend}")
            if type(subtrahend) is float:
                t = float

        return t(difference)

    def multiplication(self, *multipliers):
        self.__init__()
        product = Decimal("1")
        t = int

        if type(multipliers[0]) is list:
            multipliers = multipliers[0]
        for multiplier in multipliers:
            product *= Decimal(f"{multiplier}")
            if type(multiplier) is float:
                t = float

        return t(product)

    def division(self, dividend, *divisors):
        self.__init__()
        quotient = Decimal(f"{dividend}")
        t = int

        if type(divisors[0]) is list:
            divisors = divisors[0]

        for divisor in divisors:
            try:
                quotient = quotient / Decimal(f"{divisor}")
                if type(divisor) is float:
                    t = float
            except DivisionByZero:
                raise ZeroDivisionError(f"除数不能为零！")

        return t(quotient)

    def recursive_range_sum(self, start, end):
        if (end := Decimal(f"{end}")) <= (start := Decimal(f"{start}")):
            return start
        else:
            return self.recursive_range_sum(start, end - 1) + end

    def loop_range_sum(self, start, end):
        self.__init__()
        Sum = Decimal("0")
        t = int

        for addend in range(start, end + 1):
            Sum += Decimal(f"{addend}")
            if type(addend) is float:
                t = float

        return t(Sum)

    def power(self, *nums):
        self.__init__()
        if type(nums[0]) is list:
            nums = nums[0]
        product = Decimal(f"{nums[0]}")
        t = int

        for num in nums[1:]:
            product = pow(product, Decimal(f"{num}"))
            if type(num) is float:
                t = float

        return t(product)

    def sqrt(self, n, pow_num=2):
        self.__init__()
        if type(n) is float:
            t = float
        else:
            t = int
        n = Decimal(f"{n}")
        pow_num = Decimal(f"{pow_num}")
        return t(pow(n, 1 / pow_num))

    def factorial(self, n):
        if (n := Decimal(f"{n}")) <= 1:
            return 1
        else:
            return int(n * self.factorial(n - 1))


NC = nc = NumbersCalculator

if __name__ == '__main__':
    print(nc().addition(1, 2, 3, 435, 23, 65, 3423458, 324, 12, 434, 542345))
