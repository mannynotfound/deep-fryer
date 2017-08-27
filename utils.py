import os
import re
import tempfile
import random


def get_dimensions(input_file):
    """
    Parse a video's resolution (1024x720) and return width + height
    """
    deets = get_video_details(input_file)
    dimensions = deets['video']['resolution'].split('x')
    width = int(dimensions[0])
    height = int(dimensions[1])
    return width, height


def get_total_seconds(input_file):
    """
    Parse a video's duration (00:00:00) and convert to total seconds
    """
    deets = get_video_details(input_file)
    duration = deets['duration'].split(':')
    hours = float(duration[0])
    minutes = float(duration[1])
    seconds = float(duration[2])
    seconds += minutes * 60
    seconds += hours * 60 * 60
    return seconds


def make_random_value(val_range):
    """
    Turn an array of 2 value ranges into float rounded to 2 decimal places
    eg [2, 3] => 2.33
    """
    return round(random.uniform(*val_range), 2)


def line_break(num):
    for _ in range(num):
        print('')


def get_video_details(input_file):
    tmpf = tempfile.NamedTemporaryFile()
    os.system('ffmpeg -i {} 2> {}'.format(input_file, tmpf.name))
    lines = tmpf.readlines()
    tmpf.close()
    metadata = {}
    for l in lines:
        l = l.strip()
        if l.startswith('Duration'):
            metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
            metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
        if l.startswith('Stream #0:0'):
            metadata['video'] = {}
            metadata['video']['codec'], metadata['video']['profile'] = \
                [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
            metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
            metadata['video']['bitrate'] = re.search('(\d+ kb/s)', l).group(1)
            metadata['video']['fps'] = re.search('(\d+ fps)', l).group(1)
        if l.startswith('Stream #0:1'):
            metadata['audio'] = {}
            metadata['audio']['codec'] = re.search('Audio: (.*?) ', l).group(1)
            metadata['audio']['frequency'] = re.search(', (.*? Hz),', l).group(1)
            metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', l).group(1)

    return metadata
