#!/usr/bin/python
from datetime import timedelta
from itertools import islice
import argparse
import srt
import sdiff


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


def _get_mapping(original, new):
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

    return (start, end)


def _get_subtitles_from_file(file):
    with open(file) as my_file:
        content = my_file.read()

    return srt.parse(content)


def _get_out(text, output=None):
    if output:
        with open(output, 'w') as file:
            file.write(text)
    else:
        print(text)


def _reverse_flag(flag, body):
    return tuple()


def _reverse_dict(dictionary):
    return {y: x for x, y in dictionary.items()}


def convert(arguments):
    new_subtitles = []
    last_end = timedelta(0)

    original_srt = _get_subtitles_from_file(arguments.input)

    if arguments.sdiff:
        with open(arguments.sdiff) as sdiff_file:
            content = sdiff_file.read()
        sdiff.validate(content)
        start, end, flags = sdiff.parse(content)

        if 'strip' in flags:
            stripped_time = float(flags['strip'])
            stripped_time = timedelta(seconds=stripped_time)

            original_srt = filter(lambda s: s.start > stripped_time, original_srt)
            last_end = stripped_time

    elif arguments.original_timing and arguments.new_timing:
        original = _get_subtitles_from_file(arguments.original_timing)
        new = _get_subtitles_from_file(arguments.new_timing)

        if arguments.strip_original:
            original_srt = islice(original_srt, arguments.strip_original, None)

        start, end = _get_mapping(original, new)
    else:
        msg = 'You must either provide `sdiff` or ' \
              '`from_timing` and `to_timing` argumetns'
        raise argparse.ArgumentError(arguments.sdiff, msg)

    for subtitle in original_srt:
        duration = subtitle.end - subtitle.start
        new_start, start_proximity = _get_proximate(subtitle.start, start)
        new_end, end_proximity = _get_proximate(subtitle.end, end)

        if start_proximity < timedelta(0, 1) and start_proximity < end_proximity:
            subtitle, last_end = _set_subtitle(subtitle, duration, start=new_start)
        elif end_proximity < timedelta(0, 1):
            subtitle, last_end = _set_subtitle(subtitle, duration, end=new_end)
        elif new_subtitles:
            delay = subtitle.start - last_end
            new_start = new_subtitles[-1].end + delay
            subtitle, last_end = _set_subtitle(subtitle, duration, start=new_start)

        new_subtitles.append(subtitle)

    new_subtitles = srt.compose(new_subtitles)

    _get_out(new_subtitles, arguments.output)


def make_sdiff(arguments):
    original = _get_subtitles_from_file(arguments.original_timing)
    new = _get_subtitles_from_file(arguments.new_timing)
    flags = {}

    if arguments.strip_original:
        original = islice(original, arguments.strip_original - 1, None)
        last = next(original)
        stripped_seconds = last.end.total_seconds()
        flags['strip'] = stripped_seconds

    start, end = _get_mapping(original, new)

    composed = '# %s --> %s\n' % (arguments.original_timing, arguments.new_timing)
    composed += sdiff.compose(start, end, **flags)

    _get_out(composed, arguments.output)


def reverse_sdiff(arguments):
    with open(arguments.input) as sdiff_file:
        content = sdiff_file.read()
    sdiff.validate(content)
    start, end, flags = sdiff.parse(content)

    new_start = _reverse_dict(start)
    new_end = _reverse_dict(end)

    new_flags = {}
    for flag, body in flags.items():
        new_flags.update(_reverse_flag(flag, body))

    reversed_ = '# reversed %s\n' % arguments.input
    reversed_ += sdiff.compose(new_start, new_end, **new_flags)

    _get_out(reversed_, arguments.output)


def main():
    description = 'Script for simple creating subtitles with new timing.'
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    convert_description = 'Convert srt file to different ' \
                          'timing according to a sdiff file ' \
                          'or two subtitle files.'
    parser_c = subparsers.add_parser('convert',
                                     description=convert_description)
    parser_c.add_argument('-d', '--sdiff', type=str,
                          help='file with information about timing changes')
    parser_c.add_argument('input', type=str,
                          help='original srt file')
    parser_c.add_argument('--original-timing', type=str,
                          help='file with original timing')
    parser_c.add_argument('--new-timing', type=str,
                          help='file with wanted timing')
    parser_c.add_argument('-s', '--strip-original', type=int,
                          help='ignore the first N subtitles in the original file')
    parser_c.add_argument('-o', '--output', type=str,
                          help='name of the output sdiff file')
    parser_c.set_defaults(func=convert)

    make_sdiff_description = 'Make sdiff file from two subtitles in .srt format.' \
                             'The text of subtitles must be the same.'
    parser_ms = subparsers.add_parser('make_sdiff',
                                      description=make_sdiff_description)
    parser_ms.add_argument('original_timing', type=str,
                           help='file with original timing')
    parser_ms.add_argument('new_timing', type=str,
                           help='file with wanted timing')
    parser_ms.add_argument('-s', '--strip-original', type=int,
                           help='ignore the first N subtitles in the original file')
    parser_ms.add_argument('-o', '--output', type=str,
                           help='name of the output sdiff file')
    parser_ms.set_defaults(func=make_sdiff)

    reverse_sdiff_description = 'Reverse sdiff file, so backward conversion is possible'
    parser_rs = subparsers.add_parser('reverse_sdiff',
                                      description=reverse_sdiff_description)
    parser_rs.add_argument('input', type=str,
                           help='sdiff file')
    parser_rs.add_argument('-o', '--output', type=str,
                           help='name of the output sdiff file')
    parser_rs.set_defaults(func=reverse_sdiff)

    args = parser.parse_args()
    if args.func:
        try:
            args.func(args)
        except (FileNotFoundError, argparse.ArgumentError) as e:
            import sys
            sys.exit(str(e))


if __name__ == '__main__':
    main()
