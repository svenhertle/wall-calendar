#!/usr/bin/python3

from calendar import Calendar, CalendarError
import sys
import argparse
import colorsys

class FSCalendar(Calendar):
    BLUE = {'red': 75/255, 'green': 101/255, 'blue': 170/255}

    def __init__(self, year, birthdays, events_small, events_main):
        Calendar.__init__(self, year, "de_DE")

        # colors
        self.add_color(self.__hsv_to_rbg(355/360, 0.7, 1),
                       self.__hsv_to_rbg(355/360, 0.5, 1),
                       self.__hsv_to_rbg(355/360, 0.7, 1),
                       self.__hsv_to_rbg(355/360, 0.2, 1))
        self.add_color(self.__hsv_to_rbg(94/360, 0.7, 0.8),
                       self.__hsv_to_rbg(94/360, 0.5, 0.8),
                       self.__hsv_to_rbg(94/360, 0.7, 0.8),
                       self.__hsv_to_rbg(94/360, 0.2, 0.8))
        self.add_color(self.__hsv_to_rbg(60/360, 0.7, 1),
                       self.__hsv_to_rbg(60/360, 0.6, 1),
                       self.__hsv_to_rbg(60/360, 0.7, 1),
                       self.__hsv_to_rbg(60/360, 0.2, 1))

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
        self.print_text("M P I", self.WIDTH-100, 10, 300, FSCalendar.BLUE, "tr")

        # print year with different bases
        self.print_text(str(self.year), 2000, 50, 200, FSCalendar.BLUE)
        self.print_text(self.__to_base(self.year, 16), 0, 0, 100,
                        FSCalendar.BLUE)

    def __hsv_to_rbg(self, h, s, v):
        # h,s,v is in [0,1]
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return {'red': r, 'green': g, 'blue': b}

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
