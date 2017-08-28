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

```
Arg | Description | Default
:------- | :---------- | :----------
--video-dip, -vd | Amount of times to run the video through deep fry filter. | 3
--audio-dip, -ad | Amount of times to run the audio through deep fry filter. | 10
```

## dependencies

```bash
pip install -r requirements.txt
```
