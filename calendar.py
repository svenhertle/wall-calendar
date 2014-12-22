import cairocffi as cairo
import datetime
import locale


class CalendarError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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

    DEFAULT_COLOR = {'red': 0, 'green': 0, 'blue': 0}

    # colors
    colors = []

    def __init__(self, year, locale="de_DE"):
        # config
        self.year = year
        self.locale = locale
        self.ctx = None

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

    def add_color(self, normal, light):
        self.colors.append([normal, light])

    def __coords_space_boxes(self):
        space_x = (Calendar.WIDTH - Calendar.PADDING_LEFT -
                  Calendar.PADDING_RIGHT - 12*Calendar.BOX_WIDTH) / 11
        space_y = (Calendar.HEIGHT - Calendar.PADDING_TOP - Calendar.PADDING_BOTTOM - 32*Calendar.BOX_HEIGHT - space_x) / 30

        return (space_x, space_y)

    def __coords_month(self, date):

        space_x,space_y = self.__coords_space_boxes()

        x = Calendar.PADDING_LEFT + (date.month-1) * (space_x + Calendar.BOX_WIDTH)
        y = Calendar.PADDING_TOP
        return (x, y)

    def __coords_day(self, date):

        month_x, month_y = self.__coords_month(date)
        space_x,space_y = self.__coords_space_boxes()

        x = month_x
        y = month_y + Calendar.BOX_HEIGHT + space_x + (date.day-1) * (space_y + Calendar.BOX_HEIGHT)
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
        self.__text(date.strftime("%B"), x_center, y_center,
                    Calendar.SIZE_MONTH)

    def __print_day(self, date):
        # positions
        x, y = self.__coords_day(date)

        # rectangle
        color = None
        if len(self.colors) > 0:
            tmp = self.colors[(date.month-1) % len(self.colors)]
            if date.weekday() == 5:  # saturday
                color = tmp[1]
            elif date.weekday() == 6:  # sunday
                color = tmp[0]
        self.__rectangle(x, y, Calendar.BOX_WIDTH, Calendar.BOX_HEIGHT, color)

        # day number
        text_padding = max(0.1*Calendar.SIZE_DAY_NUMBER, 3)
        self.__text(date.strftime("%d"), x + text_padding, y + text_padding,
                    Calendar.SIZE_DAY_NUMBER, "tl")

        # weekday
        text_padding = max(0.1*Calendar.SIZE_DAY, 3)
        self.__text(date.strftime("%a"), x + Calendar.BOX_WIDTH - text_padding,
                    y + Calendar.BOX_HEIGHT - text_padding, Calendar.SIZE_DAY,
                    "br")

    def __rectangle(self, x, y, w, h, fill_color=DEFAULT_COLOR):
        self.ctx.rectangle(x, y, w, h)
        if not fill_color is None:
            self.ctx.set_source_rgb(**fill_color)
            self.ctx.fill()
            self.ctx.set_source_rgb(**Calendar.DEFAULT_COLOR)
        self.ctx.rectangle(x, y, w, h)  # lines (FIXME)
        self.ctx.stroke()

    def __text(self, text, x, y, size, relative="c"):
        # font size
        self.ctx.set_font_size(size)

        # position
        x_diff = 0
        y_diff = 0
        x_bearing, y_bearing, width, height, x_advance, y_advance = self.ctx.text_extents(text)

        if relative == "c":
            # center
            x_diff = -(width/2 + x_bearing)
            y_diff = -(height/2 + y_bearing)
        elif relative == "tl":
            # top left
            x_diff = 0
            y_diff = +height
        elif relative == "tr":
            # top right
            x_diff = -width - x_bearing
            y_diff = +height
        elif relative == "br":
            # bottom right
            x_diff = -width - x_bearing
            y_diff = 0

        self.ctx.move_to(x + x_diff, y + y_diff)

        # draw
        self.ctx.show_text(text)
