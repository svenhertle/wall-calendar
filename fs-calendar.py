#!/usr/bin/python3

from calendar import Calendar, CalendarError
import sys
import argparse

class FSCalendar(Calendar):
    BLUE = {'red': 75/255, 'green': 101/255, 'blue': 170/255}

    def __init__(self, year, birthdays, events_small, events_main):
        Calendar.__init__(self, year, "de_DE")

        # colors
        self.add_color({'red': 241/255, 'green': 72/255, 'blue': 87/255},
                       {'red': 250/255, 'green': 201/255, 'blue': 205/255})
        self.add_color({'red': 108/255, 'green': 192/255, 'blue': 41/255},
                       {'red': 211/255, 'green': 236/255, 'blue': 192/255})
        self.add_color({'red': 255/255, 'green': 253/255, 'blue': 38/255},
                       {'red': 255/255, 'green': 254/255, 'blue': 191/255})

        # data sources
        if birthdays:
            for f in birthdays:
                self.add_data(f, "top")

        if events_small:
            for f in events_small:
                self.add_data(f, "bottom")

        if events_main:
            for f in events_main:
                self.add_data(f, "main")

    def create(self, filename):
        Calendar.create(self, filename)

        # logo (FIXME)
        #self.print_text("M P I", self.WIDTH-100, 10, 300, FSCalendar.BLUE, "tr")

        # print year with different bases
        self.print_text(str(self.year), 2000, 50, 200, FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 16), 100, 175, 100,
                        FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 2), 200, 50, 100,
                        FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 8), 800, 175, 100,
                        FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 17), 1000, 50, 100,
                        FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 3), 1150, 175, 100,
                        FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 21), 1530, 50, 100,
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
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", type=int, required=True,
                        help="year of the calendar")
    parser.add_argument("-b", "--birthdays", nargs="+",
                        metavar="file", help="CSV file with birthdays")
    parser.add_argument("-e", "--events", metavar="file",
                        nargs="+",
                        help="CSV file with events, that are printed small")
    parser.add_argument("-m", "--main-events", metavar="file",
                        nargs="+",
                        help="CSV file with main events, that are printed big")
    parser.add_argument("-o", "--output", required=True, metavar="file",
                        help="output file for SVG")
    args = parser.parse_args()

    # run
    try:
        cal = FSCalendar(args.year, args.birthdays, args.events,
                         args.main_events)
        cal.create(args.output)
    except CalendarError as e:
        print(str(e))
        sys.exit(1)
