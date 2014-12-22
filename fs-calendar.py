from calendar import Calendar, CalendarError

class FSCalendar(Calendar):
    BLUE = {'red': 75/255, 'green': 101/255, 'blue': 170/255}

    def __init__(self, year):
        Calendar.__init__(self, year, "de_DE")

        # colors
        self.add_color({'red': 241/255, 'green': 72/255, 'blue': 87/255},
                       {'red': 250/255, 'green': 201/255, 'blue': 205/255})
        self.add_color({'red': 108/255, 'green': 192/255, 'blue': 41/255},
                       {'red': 211/255, 'green': 236/255, 'blue': 192/255})
        self.add_color({'red': 255/255, 'green': 253/255, 'blue': 38/255},
                       {'red': 255/255, 'green': 254/255, 'blue': 191/255})

    def create(self, filename):
        Calendar.create(self, filename)

        # print year with different bases
        self.print_text(str(self.year), 0, 0, 100, FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 16), 0, 0, 100,
                        FSCalendar.BLUE)

    def __to_base(self, number, base):
        if base < 2 or base > 36:
            return None

        div_result = number
        result = ""

        while(div_result != 0):
            digit = div_result % base
            div_result = int(div_result / base)
            result = self.__digit_str(digit) + result

        return result

    def __digit_str(self, digit):
        if digit >= 0 and digit <= 9:
            return str(digit)
        elif digit >= 10 and digit <= 35:
            return chr(65 + digit - 10)

        return None


if __name__ == "__main__":
    cal = FSCalendar(2015)
    cal.create("test.svg")
