import cairocffi as cairo
import datetime
import locale
import csv


class CalendarError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DataReader:
    """Reads calendar data from CSV file."""
    def __init__(self, year):
        self.year = year
        self.data = {}

    def read(self, filename):
        try:
            f = open(filename, 'r')
            csv_reader = csv.reader(f, dialect="excel")

            for row in csv_reader:
                # check for valid data
                if len(row) < 3 or len(row) > 4:
                    raise CalendarError("Error in file: " + filename +
                                        " (wrong number of columns)")

                # values
                month = row[0]
                day = row[1]
                text = row[2]

                # optional: highlight
                highlight = False
                if len(row) == 4 and row[3].lower() == "yes":
                        highlight = True

                # add to list
                key = datetime.date(self.year, int(month), int(day))
                if not key in self.data:
                    self.data[key] = []
                self.data[key].append([text, highlight])
        except IOError as e:
            raise CalendarError("Can't open file: " + filename + " (" +
                                str(e) + ")")
        except TypeError as e:
            raise CalendarError("Error in file: " + filename +
                                " (month must be a number)")

    def get(self, date):
        if date in self.data:
            return self.data[date]

        return []

    def get_str(self, date):
        text = map(lambda x: x[0], self.get(date))
        return ", ".join(text)

    def is_highlighted(self, date):
        highlight = False

        tmp = self.get(date)
        for d in tmp:
            highlight = highlight or d[1]

        return highlight


class Calendar:
    """ Creates a calendar as vector graphic """

    # size of A0 in points (1 point = 1/72.0 inch)
    WIDTH = 3370.39
    HEIGHT = 2383.94

    PADDING_TOP = 300
    PADDING_RIGHT = 100
    PADDING_LEFT = 100
    PADDING_BOTTOM = 50

    BOX_WIDTH = 240
    BOX_HEIGHT = 50

    SIZE_MONTH = 30
    SIZE_DAY_NUMBER = 35
    SIZE_DAY = 20
    SIZE_DATA = 10
    SIZE_DATA_MAIN = 20

    DATA_MAIN_SHIFT = 13

    DEFAULT_COLOR = {'red': 0, 'green': 0, 'blue': 0}

    # colors
    colors = []

    def __init__(self, year, locale="de_DE"):
        # config
        self.year = year
        self.locale = locale
        self.ctx = None

        self.data_top = DataReader(self.year)
        self.data_bottom = DataReader(self.year)
        self.data_main = DataReader(self.year)

    def create(self, filename):
        # init cairo
        surface = cairo.SVGSurface(filename, Calendar.WIDTH, Calendar.HEIGHT)
        self.ctx = cairo.Context(surface)

        # set locale for day and month names
        locale.setlocale(locale.LC_ALL, self.locale)

        # print month label
        for m in range(12):
            month = datetime.date(self.year, m+1, 1)
            self.__print_month_label(month)

        # print days
        day = datetime.date(self.year, 1, 1)
        delta = datetime.timedelta(1)
        while day.year == self.year:
            self.__print_day(day)
            day += delta

        # finish
        self.ctx.stroke()

    def add_color(self, month, saturday, sunday, highlight):
        self.colors.append([month, saturday, sunday, highlight])

    def add_data(self, filename, position):
        if position == "top":
            self.data_top.read(filename)
        elif position == "bottom":
            self.data_bottom.read(filename)
        elif position == "main":
            self.data_main.read(filename)
        else:
            raise CalendarError("Unknown position for data: " + position)

    def print_text(self, text, x, y, size, color=DEFAULT_COLOR, relative="tl"):
        # font size
        self.ctx.set_font_size(size)

        # position
        x_diff = 0
        y_diff = 0
        x_bearing, y_bearing, width, height, x_advance, \
            y_advance = self.ctx.text_extents(text)

        if relative == "c":  # center
            x_diff = -(width/2 + x_bearing)
            y_diff = -(height/2 + y_bearing)
        elif relative == "tl":  # top left
            y_diff = +height
        elif relative == "tr":  # top right
            x_diff = -width - x_bearing
            y_diff = +height
        elif relative == "br":  # bottom right
            x_diff = -width - x_bearing

        # set position for text
        self.ctx.move_to(x + x_diff, y + y_diff)

        # draw with color
        self.ctx.set_source_rgb(**color)
        self.ctx.show_text(text)
        self.ctx.set_source_rgb(**Calendar.DEFAULT_COLOR)

        # finish
        self.ctx.stroke()

    def __coords_space_boxes(self):
        space_x = (Calendar.WIDTH - Calendar.PADDING_LEFT -
                   Calendar.PADDING_RIGHT - 12*Calendar.BOX_WIDTH) / 11
        space_y = (Calendar.HEIGHT - Calendar.PADDING_TOP -
                   Calendar.PADDING_BOTTOM - 32*Calendar.BOX_HEIGHT -
                   space_x) / 30

        return (space_x, space_y)

    def __coords_month(self, date):

        space_x, space_y = self.__coords_space_boxes()

        x = Calendar.PADDING_LEFT + (date.month-1) * \
            (space_x + Calendar.BOX_WIDTH)
        y = Calendar.PADDING_TOP
        return (x, y)

    def __coords_day(self, date):

        month_x, month_y = self.__coords_month(date)
        space_x, space_y = self.__coords_space_boxes()

        x = month_x
        y = month_y + Calendar.BOX_HEIGHT + space_x + (date.day-1) * \
            (space_y + Calendar.BOX_HEIGHT)
        return (x, y)

    def __print_month_label(self, date):
        # positions
        x, y = self.__coords_month(date)
        x_center = x + Calendar.BOX_WIDTH / 2
        y_center = y + Calendar.BOX_HEIGHT / 2

        # rectangle
        color = None
        if len(self.colors) > 0:
            color = self.colors[(date.month-1) % len(self.colors)][0]
        self.__rectangle(x, y, Calendar.BOX_WIDTH, Calendar.BOX_HEIGHT, color)

        # text
        self.print_text(date.strftime("%B"), x_center, y_center,
                        Calendar.SIZE_MONTH, relative="c")

    def __print_day(self, date):
        # positions
        x, y = self.__coords_day(date)

        # check data for highlight
        highlight = False
        for d in [self.data_top, self.data_main, self.data_bottom]:
            highlight = highlight or d.is_highlighted(date)

        # rectangle
        color = None
        if len(self.colors) > 0:
            tmp = self.colors[(date.month-1) % len(self.colors)]
            if date.weekday() == 5:  # saturday
                color = tmp[1]
            elif date.weekday() == 6:  # sunday
                color = tmp[2]
            elif highlight:  # highlight
                color = tmp[3]
        self.__rectangle(x, y, Calendar.BOX_WIDTH, Calendar.BOX_HEIGHT, color)

        # day number
        text_padding = max(0.1*Calendar.SIZE_DAY_NUMBER, 3)
        self.print_text(date.strftime("%d"), x + text_padding,
                        y + text_padding, Calendar.SIZE_DAY_NUMBER,
                        relative="tl")

        # weekday
        text_padding = max(0.1*Calendar.SIZE_DAY, 3)
        self.print_text(date.strftime("%a"),
                        x + Calendar.BOX_WIDTH - text_padding,
                        y + Calendar.BOX_HEIGHT - text_padding,
                        Calendar.SIZE_DAY, relative="br")

        # data
        text_padding = max(0.1*Calendar.SIZE_DATA, 3)
        # top
        self.print_text(self.data_top.get_str(date),
                        x + Calendar.BOX_WIDTH - text_padding,
                        y + text_padding, Calendar.SIZE_DATA, relative="tr")
        # bottom
        self.print_text(self.data_bottom.get_str(date),
                        x + text_padding,
                        y + Calendar.BOX_HEIGHT - text_padding,
                        Calendar.SIZE_DATA, relative="bl")
        # main
        self.print_text(self.data_main.get_str(date),
                        x + Calendar.BOX_WIDTH/2 + Calendar.DATA_MAIN_SHIFT,
                        y + Calendar.BOX_HEIGHT/2, Calendar.SIZE_DATA_MAIN,
                        relative="c")

    def __rectangle(self, x, y, w, h, fill_color=None):
        # print rectangle
        self.ctx.rectangle(x, y, w, h)

        # fill with color
        if not fill_color is None:
            self.ctx.set_source_rgb(**fill_color)
            self.ctx.fill()
            self.ctx.set_source_rgb(**Calendar.DEFAULT_COLOR)

            # print border
            self.ctx.rectangle(x, y, w, h)  # lines (FIXME)

        # finish
        self.ctx.stroke()
