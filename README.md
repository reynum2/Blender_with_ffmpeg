# Blender with ffmpeg

Encode vidéo from the Blender Frame server with ffmpeg in good quality
You can use all ffmpeg option you want to create your vidéo.


# Requirements

Blender
ffmpeg
Python3 (with package urllib3)

# Usage

Launch the Blender frame server
Then launch the program with 

```
python3 encode_video.py
```

If you have an external audio (tested only with mp3 files) you can add it automaticaly with 

```
python3 encode_video.py --audio <audio_name>
```

for other option 

```
python3 encode_video.py -h
```
