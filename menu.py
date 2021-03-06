#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import collections
import datetime
import urllib2
import xml.dom.minidom

from HTMLParser import HTMLParser

MENU_RSS_URL = 'http://legacy.cafebonappetit.com/rss/menu/633'

COLOR_MAP = {
    'BLACK': "\033[30m",
    'RED': "\033[31m",
    'GREEN': "\033[32m",
    'YELLOW': "\033[33m",
    'BLUE': "\033[34m",
    'PURPLE': "\033[35m",
    'CYAN': "\033[36m",
    'WHITE': "\033[37m",
    'BOLD_BLACK': "\033[30;1m",
    'BOLD_RED': "\033[31;1m",
    'BOLD_GREEN': "\033[32;1m",
    'BOLD_YELLOW': "\033[33;1m",
    'BOLD_BLUE': "\033[34;1m",
    'BOLD_PURPLE': "\033[35;1m",
    'BOLD_CYAN': "\033[36;1m",
    'BOLD_WHITE': "\033[37;1m",
}

COLOR_RESET = "\033[0m"

class MenuParser(HTMLParser):
    '''
    Menu parser
    '''

    def __init__(self):
        self.parsed_menu = collections.defaultdict(list)
        self._cur_course = None
        self._change_cur_course = False
        self._cur_entree = None
        self._change_cur_entree = False
        self._append_cur_entree = False
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self._change_cur_course = True
        elif tag == 'h4':
            self._change_cur_entree = True
        elif tag == 'p':
            self._append_cur_entree = True

    def handle_data(self, data):
        if self._change_cur_course is True:
            if self._cur_course is not None:
                self.parsed_menu[self._cur_course].append(' '.join(self._cur_entree))
            self._cur_course = data
            self._cur_entree = None
            self._change_cur_course = False
        elif self._change_cur_entree is True:
            if self._cur_entree is not None:
                self.parsed_menu[self._cur_course].append(' '.join(self._cur_entree))
            self._cur_entree = [data.strip()]
            self._change_cur_entree = False
        elif self._append_cur_entree:
            self._cur_entree.append(data.strip())
            self._append_cur_entree = False

def get_menu():
    '''
    Return list of days, menus
    menus: course->entrees->list(entree)
    '''
    full_menu = []
    menu = urllib2.urlopen(MENU_RSS_URL)
    menu_dom = xml.dom.minidom.parse(menu)
    for item in menu_dom.getElementsByTagName('item'):
        menu_parser = MenuParser()
        title = item.getElementsByTagName('title').item(0)
        day = title.firstChild.data
        description = item.getElementsByTagName('description').item(0)

        day_menu = description.firstChild.data
        menu_parser.feed(day_menu)
        full_menu.append((day, menu_parser.parsed_menu))
    return full_menu

def color_print(color, text):
  print("{0}{1}{2}".format(COLOR_MAP[color], text, COLOR_RESET))

def print_entrees(courses, course, color):
    '''
    Entree printer
    '''
    color_print(color, course)
    color_print(color, '-' * len(course))
    entrees = courses[course]
    if len(entrees) == 0:
        print('No {0} found.'.format(course))
    for entree in sorted(entrees):
        print(entree)
    print()


def print_menu(menu, show_breakfast=False, show_lunch=False, show_dinner=False, show_week=False):
    '''
    Menu printer
    '''
    if show_breakfast is not True and show_lunch is not True and show_dinner is not True:
        # Nothing selected, so show all
        show_breakfast, show_lunch, show_dinner = True, True, True
    for (idx, (day, courses)) in enumerate(menu):
        # FIXME: Going to assume we always get 5 days
        if show_week is True or datetime.date.today().weekday() == idx:
            color_print('BOLD_WHITE', day)
            color_print('BOLD_WHITE', '=' * len(day))
            if show_breakfast is True:
                print_entrees(courses, 'Breakfast', 'YELLOW')
            if show_lunch is True:
                print_entrees(courses, 'Lunch', 'CYAN')
            if show_dinner is True:
                print_entrees(courses, 'Dinner', 'GREEN')

def main():
    '''
    Fetch the menu!
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--breakfast', action='store_true', help='show breakfast')
    parser.add_argument('-l', '--lunch', action='store_true', help='show lunch')
    parser.add_argument('-d', '--dinner', action='store_true', help='show dinner')
    parser.add_argument('-w', '--week', action='store_true', help='show week')
    args = parser.parse_args()

    menu = get_menu()
    print_menu(menu, show_breakfast=args.breakfast, show_lunch=args.lunch, show_dinner=args.dinner, show_week=args.week)

if __name__ == '__main__':
    main()
