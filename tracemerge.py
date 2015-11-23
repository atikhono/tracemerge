#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
#
# =============================================================================
#
# Copyright (c) 2015, Anna Tikhonova <anna.m.tikhonova@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# =============================================================================
#

import argparse
import os
import re


class CoverReport(object):
    def __init__(self, fname):
        self.fname = fname
        self.flines = self.__read()
        self.offset = self.__get_offset()

    def __read(self):
        fname = self.fname

        flines = []
        with open(fname, 'r') as fd:
            flines = [l.rstrip() for l in fd.readlines()]

        return flines

    def out(self):
        flines = self.flines

        for l in flines:
            print l

    def __get_offset(self):
        flines = self.flines

        for l in flines:
            m = re.search('^>+', l)
            if m:
                return len(m.group(0))

        raise Exception("Trace coverage offset ('^>+') not found in file %s" % self.fname)

    def line_exec(self, lnum):
        l = self.flines[lnum]
        off = self.offset

        if re.match('^[1-9]\d*$', l[0:off][:-1].lstrip()):
            return True

        return False

    def line_not_exec(self, lnum):
        l = self.flines[lnum]
        off = self.offset

        if re.match('^>{%s}' % off, l):
            return True

        return False

    def check(self, other):
        assert(isinstance(other, CoverReport))

        f1_name = self.fname
        f2_name = other.fname
        f1_lines = self.flines
        f2_lines = other.flines

        if len(f1_lines) != len(f2_lines):
            raise Exception("Number of lines does not match in files %s and %s" % (f1_name, f2_name))

    def merge(self, other):
        self.check(other)

        f1_lines = self.flines
        f2_lines = other.flines

        o1 = self.offset
        o2 = other.offset
        o = max(o1, o2)

        f_lines = []

        for lnum in xrange(len(f1_lines)):
            f1_line = f1_lines[lnum]
            f2_line = f2_lines[lnum]

            #
            # Strip the lines to avoid whitespaced lines mismatch.
            #
            # The first iteration generates an offset for empty lines. When the
            # next iteration runs and a new cover report file is read, rstrip()
            # in process() kills the offset of a whitespaced line:
            #
            #       '    \n'.rstrip() = ''
            #
            if f1_line.rstrip() != f2_line.rstrip():

                if self.line_not_exec(lnum) and other.line_exec(lnum):
                    # f1 '>>>>>>'
                    # f2 '    1:'
                    f_lines.append("%s%s" % (("{0:>%s}" % o).format(f2_line[0:o2]), f1_line[o1:]))
                elif self.line_exec(lnum) and other.line_not_exec(lnum):
                    # f1 '    1:'
                    # f2 '>>>>>>'
                    f_lines.append("%s%s" % (("{0:>%s}" % o).format(f1_line[0:o1]), f1_line[o1:]))
                elif self.line_exec(lnum) and other.line_exec(lnum):
                    # f1 '    1:'
                    # f1 '    2:'
                    try:
                        n = int(f1_line[0:o1][:-1].lstrip()) + int(f2_line[0:o2][:-1].lstrip())
                        f_lines.append("%s%s" % (("{0:>%s}" % o).format("%s:" % n), f1_line[o1:]))
                    except ValueError:
                        print "ValueError in '%s' + '%s'" % (f1_line[0:o1][:-1].lstrip(), f2_line[0:o2][:-1].lstrip())
                        quit()
                else:
                    raise Exception("Don't know how to process lines:\n'%s'\n'%s\n\tat %s'" % (f1_line, f2_line, lnum + 1))
                    quit()

            else:
                if self.line_exec(lnum):
                    # f1 '     1:'
                    # f2 '     1:'
                    try:
                        n = int(f1_line[0:o1][:-1].lstrip()) + int(f2_line[0:o2][:-1].lstrip())
                        f_lines.append("%s%s" % (("{0:>%s}" % o).format("%s:" % n), f1_line[o1:]))
                    except ValueError:
                        print "ValueError in '%s' + '%s'" % (f1_line[0:o1][:-1].lstrip(), f2_line[0:o2][:-1].lstrip())
                        quit()
                else:
                    # Align right to `o` spaces and attach the remainder of the line
                    f_lines.append("%s%s" % (("{0:>%s}" % o).format(f1_line[0:o1]), f1_line[o1:]))

        self.flines = f_lines


def process(files):
    try:
        cr_1 = CoverReport(files[0])

        for f in files[1:]:
            cr_2 = CoverReport(f)
            cr_1.merge(cr_2)

        return cr_1
    except Exception as e:
        print "%s: %s" % (os.path.basename(__file__), e)
        quit()

def path_to_file(path):
    if os.access(path, os.R_OK):
        return path
    raise argparse.ArgumentTypeError("%s is not a valid location or the file is not readable" % path)


def main():
    parser = argparse.ArgumentParser(description='Merge trace coverage reports')
    parser.add_argument('files', metavar='file', type=path_to_file, nargs='+', help='coverage report files to merge')
    args = parser.parse_args()

    # Remove duplicate files from the arg list
    process(list(set(args.files))).out()


if __name__ == '__main__':
    main()
