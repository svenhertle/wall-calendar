from calendar import Calendar, CalendarError

class FSCalendar(Calendar):
    def __init__(self, year):
        Calendar.__init__(self, year, "de_DE")

        # colors
        self.add_color({'red': 241/255, 'green': 72/255, 'blue': 87/255},
                       {'red': 250/255, 'green': 201/255, 'blue': 205/255})
        self.add_color({'red': 108/255, 'green': 192/255, 'blue': 41/255},
                       {'red': 211/255, 'green': 236/255, 'blue': 192/255})
        self.add_color({'red': 255/255, 'green': 253/255, 'blue': 38/255},
                       {'red': 255/255, 'green': 254/255, 'blue': 191/255})


if __name__ == "__main__":
    cal = FSCalendar(2014)
    cal.create("test.svg")
