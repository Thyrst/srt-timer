#!/usr/bin/python
from srt import srt_timestamp_to_timedelta, timedelta_to_srt_timestamp


def compose(start, end, **flags):
    '''
    Compose sdiff string from `start` and `end` dictionaries.

    >>> import datetime
    >>> input = ({datetime.timedelta(0, 143, 671000): datetime.timedelta(0, 5, 485000), datetime.timedelta(0, 235, 644000): datetime.timedelta(0, 97, 458000), datetime.timedelta(0, 251, 512000): datetime.timedelta(0, 113, 326000), datetime.timedelta(0, 287, 481000): datetime.timedelta(0, 149, 295000), datetime.timedelta(0, 334, 395000): datetime.timedelta(0, 196, 209000), datetime.timedelta(0, 339, 500000): datetime.timedelta(0, 201, 314000)}, {datetime.timedelta(0, 146, 672000): datetime.timedelta(0, 8, 486000), datetime.timedelta(0, 246, 295000): datetime.timedelta(0, 108, 109000), datetime.timedelta(0, 253, 545000): datetime.timedelta(0, 115, 359000), datetime.timedelta(0, 290, 15000): datetime.timedelta(0, 151, 829000), datetime.timedelta(0, 336, 862000): datetime.timedelta(0, 198, 676000), datetime.timedelta(0, 342, 301000): datetime.timedelta(0, 204, 115000)})
    >>> print(compose(*input, flag='Hello'), end='')
    :flag Hello
    00:02:23,671 --> 00:00:05,485 | 00:02:26,672 --> 00:00:08,486
    00:03:55,644 --> 00:01:37,458 | 00:04:06,295 --> 00:01:48,109
    00:04:11,512 --> 00:01:53,326 | 00:04:13,545 --> 00:01:55,359
    00:04:47,481 --> 00:02:29,295 | 00:04:50,015 --> 00:02:31,829
    00:05:34,395 --> 00:03:16,209 | 00:05:36,862 --> 00:03:18,676
    00:05:39,500 --> 00:03:21,314 | 00:05:42,301 --> 00:03:24,115

    '''
    string = ''
    for flag, body in flags.items():
        string += ':%s %s\n' % (flag, body)

    for start_tuple, end_tuple in zip(start.items(), end.items()):
        start_sdiff = _compose_sdiff(*start_tuple)
        end_sdiff = _compose_sdiff(*end_tuple)

        string += '%s | %s\n' % (start_sdiff, end_sdiff)

    return string


def parse(string):
    '''
    Parse `start` and `end` dictionaries from a string in sdiff file fromat.

    >>> parse("""
    ... :flag Hello
    ...
    ... 00:02:23,671 --> 00:00:05,485 | 00:02:26,672 --> 00:00:08,486
    ... 00:03:55,644 --> 00:01:37,458 | 00:04:06,295 --> 00:01:48,109
    ... 00:04:11,512 --> 00:01:53,326 | 00:04:13,545 --> 00:01:55,359
    ... 00:04:47,481 --> 00:02:29,295 | 00:04:50,015 --> 00:02:31,829
    ... 00:05:34,395 --> 00:03:16,209 | 00:05:36,862 --> 00:03:18,676
    ... 00:05:39,500 --> 00:03:21,314 | 00:05:42,301 --> 00:03:24,115
    ... """)
    ({datetime.timedelta(0, 143, 671000): datetime.timedelta(0, 5, 485000), datetime.timedelta(0, 235, 644000): datetime.timedelta(0, 97, 458000), datetime.timedelta(0, 251, 512000): datetime.timedelta(0, 113, 326000), datetime.timedelta(0, 287, 481000): datetime.timedelta(0, 149, 295000), datetime.timedelta(0, 334, 395000): datetime.timedelta(0, 196, 209000), datetime.timedelta(0, 339, 500000): datetime.timedelta(0, 201, 314000)}, {datetime.timedelta(0, 146, 672000): datetime.timedelta(0, 8, 486000), datetime.timedelta(0, 246, 295000): datetime.timedelta(0, 108, 109000), datetime.timedelta(0, 253, 545000): datetime.timedelta(0, 115, 359000), datetime.timedelta(0, 290, 15000): datetime.timedelta(0, 151, 829000), datetime.timedelta(0, 336, 862000): datetime.timedelta(0, 198, 676000), datetime.timedelta(0, 342, 301000): datetime.timedelta(0, 204, 115000)}, {'flag': 'Hello'})

    '''
    start = []
    end = []
    flags = {}
    header = True
    for line in string.split('\n'):
        line = line.strip()
        if not line:
            continue

        if header:
            if line.startswith('#'):
                continue
            elif line.startswith(':'):
                flag, body = line[1:].split(None, 1)
                flags[flag] = body
                continue
            else:
                header = False

        start_sdiff, end_sdiff = line.split(' | ')
        start.append(_parse_sdiff(start_sdiff))
        end.append(_parse_sdiff(end_sdiff))

    return (dict(start), dict(end), flags)


def _compose_sdiff(from_time, to_time):
    '''
    Parse sdiff string to tuple of timedeltas.

    >>> from datetime import timedelta
    >>> _compose_sdiff(timedelta(1, 5), timedelta(0, 8, 55555))
    '24:00:05,000 --> 00:00:08,055'

    '''
    from_timestamp = timedelta_to_srt_timestamp(from_time)
    to_timestamp = timedelta_to_srt_timestamp(to_time)

    string = '%s --> %s' % (from_timestamp, to_timestamp)
    return string


def _parse_sdiff(sdiff):
    '''
    Parse sdiff string to tuple of timedeltas.

    >>> _parse_sdiff('24:00:05,000 --> 00:00:08,055')
    (datetime.timedelta(1, 5), datetime.timedelta(0, 8, 55000))

    '''
    from_time, to_time = sdiff.split(' --> ')

    from_time = srt_timestamp_to_timedelta(from_time)
    to_time = srt_timestamp_to_timedelta(to_time)

    return (from_time, to_time)


class SDiffError(Exception):
    pass


def validate(string):
    '''
    Validate the format of sdiff string

    >>> try:
    ...     validate("""
    ...         # header
    ...         :strip 00:01:50,600
    ...         # random comment
    ...
    ...         00:05:34,395 --> 00:03:16,209 | 00:05:36,862 --> 00:03:18,676
    ...         00:05:39,500 --> 00:03:21,314 | 00:05:42,301 --> 00:03:24,115
    ...         00:06:37,758 --> 00:04:19,572 | 00:06:41,393 --> 00:04:23,207
    ...         00:07:13,827 --> 00:04:55,641 | 00:07:15,227 --> 00:04,041
    ...         00:07:37,618 --> 00:05:19,432 | 00:07:39,017 --> 00:05:20,831
    ...     """)
    ... except SDiffError as e:
    ...     print(str(e))
    ...
    line 8: Expected timestamp length >= 9, but got 12 (value: 00:04,041)

    '''
    try:
        header = True
        for i, line in enumerate(string.split('\n')):
            line = line.strip()
            if not line:
                continue

            if header:
                if line.startswith('#'):
                    continue
                elif line.startswith(':'):
                    flag_parts = line.split()
                    assert len(flag_parts[0]) > 1, 'line %d: Empty flag' % i
                    assert len(flag_parts) > 1, 'line %d: Empty flag body' % i
                    continue
                else:
                    header = False

            assert ' | ' in line, 'line %d: Missing start/end time separator (" | ")' % i

            start, end = line.split(' | ')

            assert ' --> ' in start, 'line %d: Missing original/new time separator ' \
                   'in start time (" --> ")' % i
            assert ' --> ' in end, 'line %d: Missing original/new time separator ' \
                   'in end time (" --> ")' % i

            for timestamp in (start.split(' --> ') + end.split(' --> ')):
                try:
                    srt_timestamp_to_timedelta(timestamp)
                except ValueError as e:
                    assert False, 'line %d: %s' % (i, e)

    except AssertionError as e:
        raise SDiffError(str(e))
