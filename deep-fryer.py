import os
import random
import ffmpy
import argparse
from collections import OrderedDict
from shutil import copyfile, rmtree

from utils import line_break, make_random_value, get_total_seconds, get_dimensions

TMP_FOLDER = './tmp'
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)


def create_base_args():
    return [
        '-y', # overwrite existing
        '-vb', '2M', # shitty bit rate to create compression effect
    ] + create_audio_args()


def create_audio_args():
    return ['-af', 'volume=10dB']


def create_filter_args():
    """
    Create randomized "deep fried" visual filters
    returns command line args for ffmpeg's filter flag -vf
    """
    saturation = make_random_value([2, 3])
    contrast = make_random_value([1.5, 2])
    noise = make_random_value([30, 60])

    eq_str = 'eq=saturation={}:contrast={}'.format(saturation, contrast)
    noise_str = 'noise=alls={}:allf=t'.format(noise)

    return ['-vf', ','.join([eq_str, noise_str])]


def get_random_emoji():
    """
    Return a random emoji file from './emoji'. To avoid errors when using the
    same file more than once, each file is given a random name and copied into './tmp'
    """
    emoji_choices = filter(lambda x: not x.startswith('.'), os.listdir('./emoji'))
    rand_choice = random.choice(emoji_choices)
    new_name = str(random.randint(0, 99999999)) + '.png'
    new_dest = '{}/{}'.format(TMP_FOLDER, new_name)
    copyfile('./emoji/{}'.format(rand_choice), new_dest)

    return new_dest


def get_random_emojis(amt):
    """
    Create emoji inputs, returning an OrderedDict where each key is the emoji
    comp name and the value includes size and filter str. eg:
    [emoji_4]: {
        filter_str: [4:v]scale=30:30,rotate=12*PI/180:c=none[emoji_4],
        size: 30,
    }
    """
    emojis = OrderedDict({})
    for idx in xrange(1, amt + 1):
        size = random.randint(50, 200)
        rotation = random.randint(-180, 180)

        input_comp = '{}:v'.format(idx)
        output_comp = 'emoji_{}'.format(idx)
        transform = 'scale={}:{},rotate={}*PI/180:c=none'.format(size, size, rotation)
        filter_str = '[{}]{}[{}]'.format(input_comp, transform, output_comp)

        emojis[output_comp] = {'size': size, 'filter_str': filter_str}

    return emojis


def create_emoji_filters(input_file):
    comp_name = '0:v'
    seconds = get_total_seconds(input_file)
    width, height = get_dimensions(input_file)

    emoji_filters = []
    emoji_amt = make_random_value([0.75, 0.95])
    random_emojis = get_random_emojis(int(seconds * emoji_amt))
    emoji_keys = random_emojis.keys()

    for idx, emoji in enumerate(emoji_keys):
        size = random_emojis[emoji]['size']
        filter_str = random_emojis[emoji]['filter_str']

        max_x = width - size
        max_y = height - size
        pos_x = make_random_value([0, max_x])
        pos_y = make_random_value([0, max_y])

        dur = make_random_value([2, 5])
        max_start = seconds - dur
        start = make_random_value([0, max_start])
        end = start + dur

        new_comp = 'comp_{}'.format(idx)
        overlay = "overlay={}:{}:enable='between(t, {}, {})'".format(pos_x, pos_y, start, end)
        emoji_filter = ';'.join([filter_str, '[{}][{}]{}'.format(comp_name, emoji, overlay)])

        if idx < (len(emoji_keys) - 1):
            emoji_filter += '[{}];'.format(new_comp)
            comp_name = new_comp

        emoji_filters.append(emoji_filter)

    return emoji_filters


def create_inputs(input_file, emoji_filters=[]):
    """
    Special input creator with optional emoji_filters argument
    that adds emoji input for every emoji filter passed
    """
    inputs = [(input_file, None)]
    # add an actual emoji file input for every filter created
    for _ in emoji_filters:
        inputs.append((get_random_emoji(), None))

    return OrderedDict(inputs)


def create_outputs(output_file, output_args):
    return OrderedDict([(output_file, output_args)])


def add_random_emojis(input_file):
    """
    Overlays emojis at random angles, size, durations, and start frames over a
    given input file. The amount of emojis is based on input file length.
    """
    emoji_filters = create_emoji_filters(input_file)
    inputs = create_inputs(input_file, emoji_filters)

    output_args = create_base_args()
    output_args += ['-filter_complex', ''.join(emoji_filters)]

    tmp_output = '{}/emojied_video.mp4'.format(TMP_FOLDER)
    outputs = create_outputs(tmp_output, output_args)

    ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
    try:
        ff.run()
        return tmp_output
    except Exception as e:
        line_break(3)
        print('Failed to add emojis.\n{}'.format(e))


def main(input_file, output_file):
    emojified_video = add_random_emojis(input_file)
    inputs = create_inputs(emojified_video)

    output_args = create_base_args() + create_filter_args()
    outputs = create_outputs(output_file, output_args)

    ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
    try:
        ff.run()
        line_break(3)
        print('Succesfully deep fried video at {}!'.format(output_file))
        line_break(3)
    except Exception as e:
        line_break(3)
        print('Failed to deep fry video.\n{}'.format(e))

    rmtree(TMP_FOLDER)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input_file', help='input file')
    ap.add_argument('-o', '--output_file', help='output file', default=None)
    args = ap.parse_args()

    assert args.input_file is not None, 'No input file provided...'
    assert args.output_file is not None, 'No output file provided...'

    main(args.input_file, args.output_file)
