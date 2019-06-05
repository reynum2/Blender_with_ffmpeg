#! /usr/bin/env python3

import urllib3
import re
import subprocess
import os

# Frame per second of the video
FPS = 30

#Create the http object
HTTP = urllib3.PoolManager()

def get_images(start, number):
    """Get the images from the Blender frameserver.
    :param: start the index of the frame
    :number: the number of frame to get
    """
    for i in range(start, start+number):
        img = HTTP.request('GET', '127.0.0.1:8080/images/ppm/{}.ppm'.format(i))

        with open('{}.ppm'.format(i), 'wb') as f:
            f.write(img.data)


def encode_images(start):
    """Use ffmpeg to encode the images downloaded."""
    file_name = "out_{:06d}.mp4".format(start)
    # Remove if the file already exist
    if os.path.isfile(file_name):
        os.remove(file_name)
    subprocess.run(
        ['ffmpeg',
         '-start_number', str(start),
         '-framerate', str(FPS),
         '-i', '%d.ppm',
         '-crf', '23',
         '-maxrate', '2500k',
         '-bufsize', '2500k',
         '-pix_fmt', 'yuvj420p',
         '-tune', 'film',
         '-preset', 'slow',
         file_name]
    )

def encode_mp4():
    """Use ffmpeg to encode the little mp4 in a big one."""
    file_name = "final.mp4"
    # Remove if the file already exist
    if os.path.isfile(file_name):
        os.remove(file_name)
    subprocess.run(
        ['ffmpeg',
         '-f', 'concat',
         '-i', 'list_mp4.txt',
         '-crf', '23',
         '-maxrate', '2500k',
         '-bufsize', '2500k',
         '-pix_fmt', 'yuvj420p',
         '-tune', 'film',
         '-preset', 'slow',
         file_name]
    )

def remove_images():
    """Delete all images .ppm"""
    images_lst = [im for im in os.listdir('.') if im.find('ppm')!=-1]
    for im in images_lst:
        os.remove(im)

def create_mp4_list_file():
    """Create a file with all mp4 files in the folder."""
    mp4_lst = [mp4 for mp4 in os.listdir('.') if mp4.find('.mp4')!=-1]
    mp4_lst.sort()
    with open('list_mp4.txt', 'w') as f:
        for mp4 in mp4_lst:
            f.write("file '{}'\n".format(mp4))

def mix_audio():
    """Copy the audio file with the video."""
    subprocess.run(
        ['ffmpeg',
         '-i', 'final.mp4',
         '-i', 'audio.mp3',
         '-c', 'copy',
         'output.mp4']
    )


if __name__ == "__main__":
    page = HTTP.request('GET', '127.0.0.1:8080/info.txt')
    info = page.data.decode()
    info_nb = re.findall('(\d+)', info)
    start = int(info_nb[0])
    end = int(info_nb[1])

    for i in range(start, end, FPS*10):
        frame_nb = FPS*10 if i+FPS*10 < end else end-i+1
        get_images(i, frame_nb)
        encode_images(i)
        remove_images()

    create_mp4_list_file()
    encode_mp4()
    

