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


def create_base_args(video_quality):
    return [
        '-y', # overwrite existing
        '-vb', '{}M'.format(video_quality), # default is 3, shitty bit rate to create compression effect
    ] + create_audio_args()


def increase_audio(input_audio, amt):
    output_args = ['-v', 'quiet', '-y', '-af', 'volume=3, bass=g=5, treble=g=-10']
    audio_file = None
    for idx in xrange(0, amt):
        input_file = audio_file or input_audio
        output = '{}/tmp_audio_{}.wav'.format(TMP_FOLDER, idx)
        ff = ffmpy.FFmpeg(inputs={input_file: None}, outputs={output: output_args})
        try:
            print('Frying audio on level {}...'.format(idx+1))
            ff.run()
            audio_file = output
        except Exception as e:
            line_break(3)
            print('Failed to increase audio.\n{}'.format(e))

    return audio_file


def extract_audio(input_file):
    output_args = ['-v', 'quiet', '-y', '-vn', '-acodec', 'copy']
    output = '{}/input_audio.aac'.format(TMP_FOLDER)
    ff = ffmpy.FFmpeg(inputs={input_file: None}, outputs={output: output_args})
    try:
        print('Fetching audio...')
        ff.run()
    except Exception as e:
        line_break(3)
        print('Failed to fetch audio.\n{}'.format(e))

    return output


def create_audio_args():
    return ['-v', 'quiet', '-af', 'bass=g=8, treble=g=-2, volume=10dB']


def create_filter_args():
    """
    Create randomized "deep fried" visual filters
    returns command line args for ffmpeg's filter flag -vf
    """
    saturation = make_random_value([2, 3])
    contrast = make_random_value([1.5, 2])
    noise = make_random_value([10, 20])
    gamma_r = make_random_value([1, 3])
    gamma_g = make_random_value([1, 3])
    gamma_b = make_random_value([1, 3])

    eq_str = 'eq=saturation={}:contrast={}'.format(saturation, contrast)
    eq_str += ':gamma_r={}:gamma_g={}:gamma_b={}'.format(gamma_r, gamma_g, gamma_b)
    noise_str = 'noise=alls={}:allf=t'.format(noise)
    sharpness_str = 'unsharp=5:5:3.25:5:5:3'

    return ['-vf', ','.join([eq_str, noise_str, sharpness_str])]


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


def get_random_emojis(amt, sizeMult):
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
        size = random.randint(int(0.02*sizeMult), int(0.37*sizeMult))
        rotation = random.randint(-180, 180)

        input_comp = '{}:v'.format(idx)
        output_comp = 'emoji_{}'.format(idx)
        transform = 'scale={}:{},rotate={}*PI/180:c=none'.format(size, size, rotation)
        filter_str = '[{}]{}[{}]'.format(input_comp, transform, output_comp)

        emojis[output_comp] = {'size': size, 'filter_str': filter_str}

    return emojis


def create_emoji_filters(input_file, emoji_amount, emoji_size):
    comp_name = '0:v'
    seconds = get_total_seconds(input_file)
    width, height = get_dimensions(input_file)

    emoji_filters = []
    emoji_amt = emoji_amount * make_random_value([0.75, 0.95])
    smallest_dimension = min(width, height)
    random_emojis = get_random_emojis(int(seconds * emoji_amt), (smallest_dimension * emoji_size))
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


def add_random_emojis(input_file, video_quality, emoji_amount, emoji_size):
    """
    Overlays emojis at random angles, size, durations, and start frames over a
    given input file. The amount of emojis is based on input file length.
    """
    emoji_filters = create_emoji_filters(input_file, emoji_amount, emoji_size)
    inputs = create_inputs(input_file, emoji_filters)

    output_args = ['-v', 'quiet', '-an'] + create_base_args(video_quality)

    output_args += ['-filter_complex', ''.join(emoji_filters)]

    tmp_output = '{}/emojied_video.mp4'.format(TMP_FOLDER)
    outputs = create_outputs(tmp_output, output_args)

    ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
    try:
        print('Adding emojis with multiplier {} and size {}...'.format(emoji_amount, emoji_size))
        ff.run()
        return tmp_output
    except Exception as e:
        line_break(3)
        print('Failed to add emojis.\n{}'.format(e))


def create_final_video(fried_video, boosted_audio, output_file):
    inputs = OrderedDict([
        (fried_video, None),
        (boosted_audio, None),
    ])
    outputs = OrderedDict([
        (output_file, ['-v', 'quiet', '-y', '-vcodec', 'copy']),
    ])
    ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
    try:
        print('Merging video and audio...')
        ff.run()
        line_break(3)
        print('Succesfully deep fried video to {}!'.format(output_file))
        line_break(3)
        return output_file
    except Exception as e:
        line_break(3)
        print('Failed to create final video.\n{}'.format(e))


def deep_fry_video(input_file, video_dip, emoji_amount, emoji_size, video_quality):
    emojified_video = add_random_emojis(input_file, video_quality, emoji_amount, emoji_size)
    inputs = create_inputs(emojified_video)

    output_args = create_base_args(video_quality) + create_filter_args()

    for idx in xrange(0, video_dip):
        
        output = '{}/deep_fried_{}.mp4'.format(TMP_FOLDER, idx)
        outputs = create_outputs(output, output_args)

        ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
        try:
            print('Frying video at level {}...'.format(idx+1))
            ff.run()
            inputs = create_inputs(output)
        except Exception as e:
            line_break(3)
            print('Failed to deep fry video.\n{}'.format(e))

    return output


def main(input_file, output_file, emoji_amount, emoji_size, video_quality, video_dip, audio_dip):
    extracted_audio = extract_audio(input_file)
    boosted_audio = increase_audio(extracted_audio, audio_dip)

    fried_video = deep_fry_video(input_file, video_dip, emoji_amount, emoji_size, video_quality)

    create_final_video(fried_video, boosted_audio, output_file)
    rmtree(TMP_FOLDER)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input_file', help='input file')
    ap.add_argument('-o', '--output_file', help='output file')
    ap.add_argument('-q', '--video_quality', help='specifies bitrate', default=3, type=int)
    ap.add_argument('-e', '--emoji_amount', help='emoji amount multiplier', default=1, type=int)
    ap.add_argument('-es', '--emoji_size', help='emoji size multiplier', default=1, type=float)
    ap.add_argument('-vd', '--video_dip', help='amount of times to run video through filter', default=3, type=int)
    ap.add_argument('-ad', '--audio_dip', help='amount of times to run audio through filter', default=10, type=int)
    args = ap.parse_args()

    assert args.input_file is not None, 'No input file provided...'
    assert args.output_file is not None, 'No output file provided...'

    main(args.input_file, args.output_file, args.emoji_amount, args.emoji_size, args.video_quality, args.video_dip, args.audio_dip)
