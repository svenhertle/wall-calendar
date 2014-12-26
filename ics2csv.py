#!/usr/bin/python3

import argparse
from icalendar import Calendar


class ConversionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def convert_ics_csv(in_file, out_file, year):
    try:
        # read input file
        f = open(in_file, 'rb')
        cal = Calendar.from_ical(f.read())
        f.close()

        # open output file
        out = open(out_file, 'w')

        # iterate over all events
        for event in cal.walk('vevent'):
            summary = event['SUMMARY']
            day = event['DTSTART'].dt
            if day.year == year:
                out.write(str(day.month) + "," + str(day.day) + ",\"" +
                          summary + "\",no\n")

        # close file
        out.close()
    except IOError as e:
        raise ConversionError("Can't open file: " + in_file + " (" + str(e) +
                              ")")

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, metavar="csv",
                        help="output file for CSV date")
    parser.add_argument("-o", "--output", required=True, metavar="csv",
                        help="output file for CSV date")
    parser.add_argument("-y", "--year", type=int, required=True,
                        help="year of the calendar")
    args = parser.parse_args()

    # convert
    convert_ics_csv(args.input, args.output, args.year)
