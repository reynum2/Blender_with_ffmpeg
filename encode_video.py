#! /usr/bin/env python3
""" Connect to a Blender frame server and create a H264 vidéo."""

import urllib3
import re
import subprocess
import os
import argparse

from sys import exit



#Create the http object
HTTP = urllib3.PoolManager()


def get_images(start, number, addr, port):
    """Get the images from the Blender frameserver.
    :param start: the index of the first frame
    :param number: the number of frame to get
    """
    for i in range(start, start+number):
        img = HTTP.request(
            'GET', "{}:{}/images/ppm/{}.ppm".format(addr, port, i)
        )

        with open('{}.ppm'.format(i), 'wb') as f:
            f.write(img.data)


def encode_images(start, fps):
    """Use ffmpeg to encode the images downloaded."""
    file_name = "out_{:06d}.mp4".format(start)
    # Remove if the file already exist
    if os.path.isfile(file_name):
        os.remove(file_name)
    subprocess.run(
        ['ffmpeg',
         '-start_number', str(start),
         '-framerate', str(fps),
         '-i', '%d.ppm',
         '-crf', '23',
         '-maxrate', '2500k',
         '-bufsize', '2500k',
         '-pix_fmt', 'yuvj420p',
         '-tune', 'film',
         '-preset', 'slow',
         file_name]
    )


def encode_mp4(file_name):
    """Use ffmpeg to encode the little mp4 in a big one."""
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
    mp4_lst = [mp4 for mp4 in os.listdir('.') if mp4.find('.mp4')!=-1 and 
               mp4.find('out_')!=-1]
    mp4_lst.sort()
    with open('list_mp4.txt', 'w') as f:
        for mp4 in mp4_lst:
            f.write("file '{}'\n".format(mp4))


def mix_audio(audio_file, video_file, final_file):
    """Copy the audio file with the video.
    
    :param audio_file: the audio file name to copy in the video
    :type audio_file: String
    :param video_file: the video file name where the audio will be copy
    :type video_file: String
    :param final_file: the output video file name
    :type final_file: String
    """
    # Remove if the final file already exist
    if os.path.isfile(final_file):
        os.remove(final_file)
    subprocess.run(
        ['ffmpeg',
         '-i', video_file,
         '-i', audio_file,
         '-c', 'copy',
         final_file]
    )


def get_info(addr="127.0.0.1", port="8080"):
    """Get the info.txt file and parse it.
    :param addr: the address where is binded the frameserver
    :type addr: String
    :param port: the port of the frameserver
    :type port: String
    """
    try:
        page = HTTP.request('GET', "{}:{}/info.txt".format(addr, port))
    except Exception as ex:
        print("{}\n{}".format(ex, "The Frame server is not unavailable"))
        exit(1)

    info = page.data.decode()
    info_nb = re.findall('(\d+)', info)
    start = int(info_nb[0])
    end = int(info_nb[1])
    return (start, end)


def main_loop(start, end, addr="127.0.0.1", port="8080", fps=30):
    """The loop that will get frame and create video with them.i
    
    :param start: The number of the first frame
    :param end: The number of the last frame
    """
    for i in range(start, end, fps*10):
        frame_nb = fps*10 if i+fps*10 < end else end-i+1
        get_images(i, frame_nb, addr, port)
        encode_images(i, fps)
        remove_images()


if __name__ == "__main__":

    #Argument parser 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audio", help="The audio file to copy into the final video",
        type=str)
    parser.add_argument(
        "--video_na", help="The video file name without audio",
        type=str, default="full_video.mp4")
    parser.add_argument(
        "--final_video", help="The final video file name with audio",
        type=str, default="final_video.mp4")
    parser.add_argument(
        "--address", help="The address where is bind the Frame server " \
        "(default 127.0.0.1)",
        type=str, default="127.0.0.1")
    parser.add_argument(
        "--port", help="The pôrt where is bind the Frame server (default 8080)",
        type=str, default="8080")
    parser.add_argument(
        "--fps", help="The Frame rate of the original video (default 30)",
        type=int, default="30")
    args = parser.parse_args()
    #print(args)

    #Get the first and last frame number
    start, end = get_info(args.address, args.port)

    #Launch the main loop
    main_loop(start, end, args.address, args.port, args.fps)

    #Create a file with all little video names
    create_mp4_list_file()
    #Make the final video file
    encode_mp4(args.video_na)

    #Copy the audio in the video
    if args.audio:
        mix_audio(args.audio, args.video_na, args.final_video)
    

# Web site to have x264 ffmpeg option
# https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping
