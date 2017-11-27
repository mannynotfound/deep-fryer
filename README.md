# deep fryer

<p align="center">
  <img width="80%" src="cover.png" />
</p>

Wrapper around `ffmpeg` to automatically give videos the [deep fried meme](http://knowyourmeme.com/memes/deep-fried-memes) effect.

## usage

```bash
python deep-fryer.py -i data/sample.mp4 -o data/deep_fried_sample.mp4
```


## optional parameters

Arg | Description | Default
:------- | :---------- | :----------
--video\_dip, -vd | Amount of times to run the video through deep fry filter. | 3
--audio\_dip, -ad | Amount of times to run the audio through deep fry filter. | 10
--emoji\_amount, -e | Multiplier of amount of emojis added to video. | 1
--emoji\_size, -es | Multiplier of random size of emojis added to video. | 1
--quality, -q | Quality of the video when run through the filter (smaller = faster frying time) | 3

## dependencies

```bash
pip install -r requirements.txt
```
