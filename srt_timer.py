#!/usr/bin/python
import argparse
import srt
import sdiff
from datetime import timedelta
from itertools import islice


def _get_proximate(time, sdiff_dict):
    new_time = None
    proximity = None

    for original, new in sdiff_dict.items():
        my_proximity = abs(time - original)

        if not new_time or proximity > my_proximity:
            new_time = new
            proximity = my_proximity

    return (new_time, proximity)


def _set_subtitle(subtitle, duration, start=None, end=None):
    last_end = subtitle.end

    if start:
        subtitle.start = start
        subtitle.end = start + duration
    elif end:
        subtitle.start = end - duration
        subtitle.end = end

    return subtitle, last_end


def convert(arguments):

    with open(arguments.sdiff) as sdiff_file:
        content = sdiff_file.read()
    sdiff.validate(content)
    start, end, flags = sdiff.parse(content)

    with open(arguments.input) as input_file:
        content = input_file.read()
    original = srt.parse(content)

    new = []
    last_end = timedelta(0)

    if 'strip' in flags:
        stripped_time = float(flags['strip'])
        stripped_time = timedelta(seconds=stripped_time)

        original = filter(lambda s: s.start > stripped_time, original)
        last_end = stripped_time

    for subtitle in original:
        duration = subtitle.end - subtitle.start
        new_start, start_proximity = _get_proximate(subtitle.start, start)
        new_end, end_proximity = _get_proximate(subtitle.end, end)

        if start_proximity < timedelta(0, 1) and start_proximity < end_proximity:
            subtitle, last_end = _set_subtitle(subtitle, duration, start=new_start)
        elif end_proximity < timedelta(0, 1):
            subtitle, last_end = _set_subtitle(subtitle, duration, end=new_end)
        elif new:
            delay = subtitle.start - last_end
            new_start = new[-1].end + delay
            subtitle, last_end = _set_subtitle(subtitle, duration, start=new_start)

        new.append(subtitle)

    new_subtitles = srt.compose(new)

    if arguments.output:
        with open(arguments.output, 'w') as output:
            output.write(new_subtitles)
    else:
        print(new_subtitles)


def make_sdiff(arguments):
    with open(arguments.original_timing) as original_file:
        content = original_file.read()
    original = srt.parse(content)
    if arguments.strip_original:
        original = islice(original, arguments.strip_original - 1, None)
        last = next(original)
        stripped_seconds = last.end.total_seconds()

    with open(arguments.new_timing) as new_file:
        content = new_file.read()
    new = srt.parse(content)
    new = list(new)

    start = {}
    end = {}
    for old_subtitle in original:
        for subtitle in new:
            if subtitle.content == old_subtitle.content:
                start[old_subtitle.start] = subtitle.start
                end[old_subtitle.end] = subtitle.end
                new.remove(subtitle)
                break

    composed = sdiff.compose(start, end)

    if arguments.output:
        with open(arguments.output, 'w') as output:
            output.write('# %s --> %s\n' %
                         (arguments.original_timing, arguments.new_timing))
            if arguments.strip_original:
                output.write(':strip %s\n' % stripped_seconds)
            output.write(composed)
    else:
        print(composed)

if __name__ == '__main__':
    description = 'Script for simple creating subtitles with new timing.'
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    subparsers.required = True

    convert_description = 'Convert srt file to different ' \
                          'timing according to a sdiff file.'
    parser_convert = subparsers.add_parser('convert',
                                           description=convert_description)
    parser_convert.add_argument('sdiff', type=str,
                                help='file with information about timing changes')
    parser_convert.add_argument('input', type=str,
                                help='original srt file')
    parser_convert.add_argument('-o', '--output', type=str,
                                help='name of the new srt file')
    parser_convert.set_defaults(func=convert)

    make_sdiff_description = 'Make sdiff file from two subtitles in .srt format.' \
                             'The text of subtitles must be the same.'
    parser_make_sdiff = subparsers.add_parser('make_sdiff',
                                              description=make_sdiff_description)
    parser_make_sdiff.add_argument('original_timing', type=str,
                                   help='file with original timing')
    parser_make_sdiff.add_argument('new_timing', type=str,
                                   help='file with wanted timing')
    parser_make_sdiff.add_argument('-s', '--strip-original', type=int,
                                   help='ignore the first N subtitles '
                                        'in the original file')
    parser_make_sdiff.add_argument('-o', '--output', type=str,
                                   help='name of the output sdiff file')
    parser_make_sdiff.set_defaults(func=make_sdiff)

    args = parser.parse_args()
    if args.func:
        args.func(args)
