#!/usr/bin/env python3

from __future__ import print_function

import requests
import sys, os, re, time
from signal import signal, SIGPIPE, SIG_DFL

VERSION = "0.1.2"

signal(SIGPIPE,SIG_DFL)

class Cl:
    '''ANSI/VT100 colors'''
    RESET     = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERSE   = '\033[7m'

    LRED      = '\033[91m'
    LGREEN    = '\033[92m'
    LYELLOW   = '\033[93m'
    LBLUE     = '\033[94m'
    LMAGENTA  = '\033[95m'
    LCYAN     = '\033[96m'

    BRED      = '\033[41m'
    BGREEN    = '\033[42m'
    BYELLOW   = '\033[43m'
    BBLUE     = '\033[44m'
    BMAGENTA  = '\033[45m'
    BCYAN     = '\033[46m'

    DRED      = '\033[31m'
    DGREEN    = '\033[32m'
    DYELLOW   = '\033[33m'
    DBLUE     = '\033[34m'
    DMAGENTA  = '\033[35m'
    DCYAN     = '\033[36m'

    # 256 colors
    #   See example: https://stackoverflow.com/questions/287871/print-in-terminal-with-colors/50025330#50025330
    fg_col = lambda color: "\33[38;5;" + str(color) + "m"
    bg_col = lambda color: "\33[48;5;" + str(color) + "m"

    fg = lambda text, color: Cl.fg_col(color) + text + Cl.RESET
    bg = lambda text, color: Cl.bg_col(color) + text + Cl.RESET

    bold = lambda s: Cl.BOLD + s + Cl.RESET
    red = lambda s: Cl.LRED + s + Cl.RESET
    gray = lambda s: Cl.fg(s, 245)

    #title = lambda s: Cl.BGREEN + s + Cl.RESET
    title = lambda s: Cl.bg(s, 88)

def get_rfc_text(num):
    '''Retrieve the plain text of RFC'''
    rfc_path = os.path.join(os.path.expanduser('~'), '.local/share/rfc/')
    rfc_fn = os.path.join(rfc_path, 'rfc{}.txt'.format(num))

    # Check on this machine
    if os.path.exists(rfc_path):
        if os.path.exists(rfc_fn):
            try:
                txt = open(rfc_fn,'r').read()
                print(Cl.gray('Found at: ' + rfc_fn))
                if txt:
                    return txt
                else:
                    print("EMPTY")
            except Exception as e:
                print("Couldn't read {}:".format(rfc_fn),e)

    # Fetch from the Internet
    t = time.time()
    url = 'https://www.ietf.org/rfc/rfc{}.txt'.format(num)
    r = requests.get(url)
    t = time.time() - t

    print (Cl.gray("URL: "+url))
    print (Cl.gray("Grabbed in {:.1f} s".format(t)))
    #print (Cl.gray("Status: " + str(r.status_code)))
    #print (Cl.gray("Content-type: " + str(r.headers['content-type'])))
    text = r.text

    # Save locally
    try:
        if not os.path.exists(rfc_path):
            os.makedirs(rfc_path)
        open(rfc_fn,'w').write(text)
        print("Saved locally")
    except:
        pass

    return text

class RFCParser:
    '''
    A class for doing basic plain text RFC parsing and coloring
    '''
    # Precompiled regular expressions
    re_page_num = re.compile(r'\[\s*Page\s+(\d+|[ivxlc]+)\s*\]', re.I)
    re_toc = re.compile(r'^\s*Table\s+of\s+contents\s*$',re.I)
    re_hat_rfc = re.compile(r'((?:RFC|Request for Comments):\s*)(\d+)', re.I)
    re_hat_obs = re.compile(r'((?:Obsoletes|Replaces):\s*)(\d+(,\s*)?)+', re.I)
    re_hat_upd = re.compile(r'((?:Updates):\s*)(\d+(,\s*)?)+', re.I)
    re_hat_cat = re.compile(r'((?:Category):\s*)(.+?)(\s{3}|$|\x1b\[)', re.I)
    re_toc_chapter = re.compile(r'^(\s*)((?:\d+\.?)+|[A-Z])?(\s+)(\w.*?\w)((?:\s*\.){4,}\s*)(\d+)\s*$')
    re_chapter = re.compile(r'^(\s*)((?:\d+\.?)+|[A-Z])?(\s+)(\w.*?\w)\s*$')
    re_rfc = re.compile(r'(RFC)(\s{0,1})(\d+)')

    # Coloring
    HAT_COLOR = 42
    OBSOLETE_COLOR = 202
    UPDATED_COLOR = 11
    THIS_COLOR = 14
    CATEGORY_COLOR = 200
    RFC_COLOR = 177
    OTHER_RFC_COLOR = 45

    def __init__(self, text=None):
        # Line numbers
        self.hat = []
        self.title = []         # title (line numbers)
        self.toc_lines = []

        self.obsoleted = []     # list of RFC numbers (as strings) that are obsoleted by this document
        self.updated = []       # list of RFC numbers (as strings) that are updated by this document

        self.rfc = None         # number of RFC as parsed
        self.bottom = None      # line with page number
        self.top_lines = None
        self.toc_start = None   # line number at which TOC starts
        self.toc_end = None     # line number at which TOC ends
        self.width = None       # by rightmost character position
        self.indents = {}
        self.chapters = []      # pairs (num,title,page)
        if text:
            self.analyze(text)

    def rfc_num_color(self, match):
        def color(num):
            if num in self.obsoleted: return self.OBSOLETE_COLOR
            if num in self.updated: return self.UPDATED_COLOR
            return self.OTHER_RFC_COLOR
        return Cl.fg(match.group(1), self.RFC_COLOR) + \
               match.group(2) + \
               Cl.fg(match.group(3), color(match.group(3)))

    @staticmethod
    def what_indent(line):
        indent = 0
        while indent<len(line) and line[indent].isspace():
            indent += 1
        return indent

    def is_chapter(self, line, last_page):
        sch = self.re_chapter.search(line)
        next_page = lambda x: str(int(x)+1) if x and x.isdigit() else x
        if sch:
            num, title = [sch.group(x) for x in [2,4]]
            if num: num = num.rstrip('.')
            if [t for n,t,p in self.chapters if (not n or n==num or next_page(last_page)==p) and t==title]:
                return True
        return False

    def analyze(self, text):
        self.top_lines = {}      # line->[count,{}], where {} are next lines in the same form
        top_line_pointer = None
        lines = text.split('\n')

        # Pass 1: find hat, TOC, width, repeating lines
        hat_ended = False
        title_ended = False
        toc_found = False
        for nl, line in zip(range(len(lines)),lines):
            line = line.rstrip()
            if not line:
                if self.hat: hat_ended = True
                if self.title: title_ended = True
                continue

            if not hat_ended:
                self.hat = (self.hat or []) + [nl]
            elif not title_ended:
                self.title = (self.title or []) + [nl]

            # Analyze width
            if self.width is None or len(line)>self.width:
                self.width = len(line)

            # Analyze repeating lines after page number
            if self.re_page_num.search(line):
                top_line_pointer = self.top_lines
            elif top_line_pointer is not None:
                # Increase counter
                if line in top_line_pointer:
                    top_line_pointer[line][0] += 1
                else:
                    top_line_pointer[line] = [1,{}]
                # Proceed to next node
                top_line_pointer = top_line_pointer[line][1]

            # TOC
            # TODO: allow TOC lines with no dots as in RFC 3261 (10.2.1.1)
            # TODO: allow multiline headers as in RFC 2617
            if not toc_found and self.re_toc.search(line):
                toc_found = True

        # Pass 2: analyze indentations, TOC chapters
        self.indents = {}
        toc = None
        top_line_pointer = None
        last_page = None
        for nl, line in zip(range(len(lines)),lines):
            line = line.rstrip()
            if not line or nl in self.hat:
                continue

            # Repeating lines after page number
            sch = self.re_page_num.search(line)
            if sch:
                last_page = sch.group(1)
                top_line_pointer = self.top_lines
                continue
            if top_line_pointer and line in top_line_pointer and top_line_pointer[line][0]>1:
                top_line_pointer = top_line_pointer[line][1]
                continue

            # Current indent
            indent = self.what_indent(line)
            if indent in self.indents:
                self.indents[indent] += 1
            else:
                self.indents[indent] = 1

            # TOC
            if toc_found:
                if toc is None and self.re_toc.search(line):
                    toc = True
                elif toc == True:
                    sch = self.re_toc_chapter.search(line)
                    if sch:
                        self.toc_lines = (self.toc_lines or []) + [nl]
                        num,title,page = [sch.group(x) for x in [2,4,6]]
                        if num: num = num.rstrip('.')
                        self.chapters.append((num or None,title,page))
                    elif self.is_chapter(line, last_page):
                        #print(Cl.fg(str(self.toc_lines), 9))
                        toc = False

        self.main_indent = min(self.indents.items(), key=lambda x: (-x[1],x[0]))[0]
        self.min_indent = min(self.indents.keys())

    def color(self, text):
        if self.width is None:      # analyze text if not already done so
            self.analyze(text)
        # Do coloring
        lines = text.split('\n')
        r = ''
        top_line_pointer = None
        last_page = None
        t = time.time()
        for nl, line in zip(range(len(lines)),lines):
            line = line.rstrip()
            indent = self.what_indent(line)

            # SWITCH

            # Empty line
            if not line:
                r += line + '\n'
                last_empty = True

            # Hat
            elif nl in self.hat:
                line = Cl.fg(line, self.HAT_COLOR) + '\n'

                # Obsolete
                match = self.re_hat_obs.search(line)
                if match:
                    self.obsoleted = [x.strip() for x in match.group(2).split(',')]
                    line = self.re_hat_obs.sub("\\1" + Cl.RESET + Cl.fg("\\2", self.OBSOLETE_COLOR) + Cl.fg_col(self.HAT_COLOR), line)

                # Updated
                match = self.re_hat_upd.search(line)
                if match:
                    self.updated = [x.strip() for x in match.group(2).split(',')]
                    line = self.re_hat_upd.sub("\\1" + Cl.RESET + Cl.fg("\\2", self.UPDATED_COLOR) + Cl.fg_col(self.HAT_COLOR), line)

                # This RFC's number
                if self.re_hat_rfc.search(line):
                    line = self.re_hat_rfc.sub("\\1" + Cl.RESET + Cl.fg("\\2", self.THIS_COLOR) + Cl.fg_col(self.HAT_COLOR), line)

                # Category
                # TODO: for RFC 2549 make it more elegant
                if self.re_hat_cat.search(line):
                    line = self.re_hat_cat.sub("\\1" + Cl.RESET + Cl.fg("\\2", self.CATEGORY_COLOR) + Cl.fg_col(self.HAT_COLOR) + "\\3", line)

                r += line

            # Title
            elif nl in self.title:
                actual_text = line.lstrip()
                spaces = line[:-len(actual_text)]
                r += spaces + Cl.title(actual_text) + '\n'

            # Page number
            elif self.re_page_num.search(line):
                last_page = self.re_page_num.search(line).group(1)
                r += Cl.fg(line, 36) + '\n'
                top_line_pointer = self.top_lines

            # Repeating lines after page number
            elif top_line_pointer and line in top_line_pointer and top_line_pointer[line][0]>1:
                r += Cl.fg(line, 36) + '\n'
                top_line_pointer = top_line_pointer[line][1]

            # TOC chapters
            elif nl in self.toc_lines:
                TOC_NUM_COL = 253
                TOC_TITLE_COL = 255
                TOC_DOTS_COL = 248
                TOC_PAGE_COL = 254
                r += self.re_toc_chapter.sub("\\1" + Cl.fg("\\2",TOC_NUM_COL) + \
                                             "\\3\\4" + \
                                             Cl.fg("\\5",TOC_DOTS_COL) + \
                                             Cl.fg("\\6",TOC_PAGE_COL), line) + \
                                             "\n"
                #sch = self.re_toc_chapter.search(line)
                #r += line + "\n"

            # Chapter?
            elif self.is_chapter(line, last_page):
                #r += Cl.fg(line, 13) + "\n"
                r += Cl.BOLD + line + Cl.RESET + "\n"

            # Topic?
            elif self.main_indent and indent==self.min_indent:
                #r += Cl.BOLD + line + Cl.RESET + '\n'
                r += Cl.fg(line, 14) + "\n"

            # Default: as is
            else:
                r += self.re_rfc.sub(self.rfc_num_color,line) + '\n'        # TODO: allow multiline RFC numbers

            last_line = line

        return r

def color_rfc(text):
    '''Return ANSI/VT100 colored text'''
    parser = RFCParser()
    return parser.color(text)

if __name__=="__main__":
    text = get_rfc_text(sys.argv[1])
    print(color_rfc(text), flush=True)

