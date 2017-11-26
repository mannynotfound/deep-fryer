import os
import re
import tempfile
import random
import time

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
    """
    Returns metadata from given file uusing ffmpeg and a temp file.
    """
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    tempname = tmpf.name
    tmpf.close()
    os.system('ffmpeg -i \"{}\" 2> {}'.format(input_file, tempname))
    tmpf.file = open(tempname)
    lines = tmpf.readlines()
    tmpf.close()
    tmpf.delete
    metadata = {}
    for l in lines:
        l = l.strip()
        if l.startswith('Duration'):
            metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
            metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
        if re.match('Stream #.*Video:',l):
            metadata['video'] = {}
            metadata['video']['codec'], metadata['video']['profile'] = \
                [e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
            metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
            metadata['video']['bitrate'] = re.search('(\d+ kb/s)', l).group(1)
            metadata['video']['fps'] = re.search('(\d+ fps)', l).group(1)
        if re.match('Stream #.*Audio:',l):
            metadata['audio'] = {}
            metadata['audio']['codec'] = re.search('Audio: (.*?) ', l).group(1)
            metadata['audio']['frequency'] = re.search(', (.*? Hz),', l).group(1)
            metadata['audio']['bitrate'] = re.search(', (\d+ kb/s)', l).group(1)

    return metadata
