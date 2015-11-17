#!/usr/bin/python
import argparse
import os
import re


def get_offset(lines):
    for l in xrange(len(lines)):
        m = re.search('^>+', lines[l])
        if m:
            return len(m.group(0))
    return None


def line_exec(l, off):
    if re.match('^[1-9]\d*$', l[0:off][:-1].lstrip()):
        return True
    return False


def line_not_exec(l, off):
    if re.match('^>{%s}' % off, l):
        return True
    return False


def process(files):
    with open(files[0], 'r') as fd:
        f1_lines = [l.rstrip() for l in fd.readlines()]

    for f in files[1:]:
        with open(f, 'r') as fd:
            f2_lines = [l.rstrip() for l in fd.readlines()]

        if len(f1_lines) != len(f2_lines):
            print "Number of lines in %s and %s does not match" % (files[0], files[1])
            quit()
        f1_lines = process_2(f1_lines, f2_lines)

    return f1_lines


def process_2(f1_lines, f2_lines):
    f_lines = []

    o1 = get_offset(f1_lines)
    o2 = get_offset(f2_lines)
    if o1 is None or o2 is None:
        print "No trace cover offset ('^>+') found in file"
        quit()
    o = max(o1, o2)

    for l in xrange(len(f1_lines)):
        #
        # Strip the lines to avoid whitespaced lines mismatch.
        #
        # The first iteration generates an offset for empty lines. When the
        # next iteration runs and a new cover report file is read, rstrip()
        # in process() kills the offset of a whitespaced line:
        #
        #       '    \n'.rstrip() = ''
        #
        if f1_lines[l].rstrip() != f2_lines[l].rstrip():

            if line_not_exec(f1_lines[l], o1) and line_exec(f2_lines[l], o2):
                # f1 '>>>>>>'
                # f2 '    1:'
                f_lines.append("%s%s" % (("{0:>%s}" % o).format(f2_lines[l][0:o2]), f1_lines[l][o1:]))
            elif line_exec(f1_lines[l], o1) and line_not_exec(f2_lines[l], o2):
                # f1 '    1:'
                # f2 '>>>>>>'
                f_lines.append("%s%s" % (("{0:>%s}" % o).format(f1_lines[l][0:o1]), f1_lines[l][o1:]))
            elif line_exec(f1_lines[l], o1) and line_exec(f2_lines[l], o2):
                # f1 '    1:'
                # f1 '    2:'
                try:
                    n = int(f1_lines[l][0:o1][:-1].lstrip()) + int(f2_lines[l][0:o2][:-1].lstrip())
                    f_lines.append("%s%s" % (("{0:>%s}" % o).format("%s:" % n), f1_lines[l][o1:]))
                except ValueError:
                    print "ValueError in '%s' + '%s'" % (f1_lines[l][0:o1][:-1].lstrip(), f2_lines[l][0:o2][:-1].lstrip())
                    quit()
            else:
                raise Exception("Don't know how to process lines at %s:\n'%s'\n'%s'" % (l+1, f1_lines[l], f2_lines[l]))

        else:
            if line_exec(f1_lines[l], o1):
                # f1 '     1:'
                # f2 '     1:'
                try:
                    n = int(f1_lines[l][0:o1][:-1].lstrip()) + int(f2_lines[l][0:o2][:-1].lstrip())
                    f_lines.append("%s%s" % (("{0:>%s}" % o).format("%s:" % n), f1_lines[l][o1:]))
                except ValueError:
                    print "ValueError in '%s' + '%s'" % (f1_lines[l][0:o1][:-1].lstrip(), f2_lines[l][0:o2][:-1].lstrip())
                    quit()
            else:
                # Align right to `o` spaces and attach the remainder of the line
                f_lines.append("%s%s" % (("{0:>%s}" % o).format(f1_lines[l][0:o1]), f1_lines[l][o1:]))

    return f_lines


def path_to_file(path):
    if os.access(path, os.R_OK):
        return path
    raise argparse.ArgumentTypeError("%s is not a valid location or the file is not readable" % path)


def main():
    parser = argparse.ArgumentParser(description='Merge trace coverage reports')
    parser.add_argument('files', metavar='file', type=path_to_file, nargs='+', help='coverage report files to merge')
    args = parser.parse_args()

    # Remove duplicate files from the arg list
    for l in process(list(set(args.files))):
        print l


if __name__ == '__main__':
    main()
