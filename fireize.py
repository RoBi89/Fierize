#!/usr/bin/python3

import subprocess
import sys
import os
from subprocess import check_output
import shlex

supportedExtensions = 'mkv', 'avi', 'mp4', '3gp', 'mov', 'mpg', 'mpeg', 'qt', 'wmv', 'm2ts'

supportedContainers = "('MPEG-4' 'Matroska')"
unSupportedContainers = ('BDAV' 'AVI' 'Flash Video')

supportedVideoCodecs = ('AVC')
unSupportedVideoCodecs = ('MPEG-4 Visual' 'xvid' 'MPEG Video')

supportedAudioCodecs = ('AAC' 'MPEG Audio' 'Vorbis' 'Ogg' 'VorbisVorbis')
unSupportedAudioCodecs = ('AC-3' 'DTS' 'PCM')

DEFAULT_VCODEC = "h264"
DEFAULT_ACODEC = "libvorbis"
DEFAULT_GFORMAT = "mkv"

changeContainer = 0
reencodeVideo = 0
reencodeAudio = 0
containerformat = ""

input = sys.argv[1]


def checkArguments():  # This is used to test if the program was called with a file or directory argument
    global input
    array = sys.argv
    if len(array) > 2 or len(array) <= 1:  # Did the user enter the right amount of arguments?
        print("Please append exactly one file or directory to the program call")
    elif os.path.isfile(input):  # It's a file
        if input.endswith(tuple(supportedExtensions)):  # Check to see if the file extension is supported
            checkGformat(input)
        else:
            print("This file type is not supported")
    elif os.path.isdir(input):  # It's a directory
        for file in os.listdir(input):  # We need to run the program on every single file inside that folder
            print(file)
            if file.endswith(tuple(supportedExtensions)):
                checkGformat(file)
            else:
                print("{}: This file type is not supported".format(file))
    else:  # It's something else
        print("Unknown input, please append a file or directory to the program call")


def checkGformat(file):  # Checks if the current gformat is supported by the fire stick
    global input
    global changeContainer
    global containerformat
    filename = os.path.join(input, file)
    print(filename)

    try:
        s = check_output(['mediainfo', '--Inform=General;%Format%', filename])  # Gets the output from mediainfo
    except OSError as e:  # Some error happened
        if e.errno == os.errno.ENOENT:  # mediainfo is not installed
            print("mediainfo does not seem to be installed. Please install it if you want to run this script")
        else:  # Something else went wrong
            raise

    s1 = s[:-1]  # Removes the second line from output
    name = s1.decode("utf-8")  # s1 is a bytes object but we need a string for the check
    print("Container: {}".format(name))
    if not name:
        print("name is empty")
    elif name in supportedContainers:  # Is the container supported by the fire stick?
        print("Container looks fine")
        changeContainer = 0
        containerformat = "name"
    else:
        print("Container needs to be changed")
        changeContainer = 1
    checkVcodec(file)


def checkVcodec(file):  # Checks if the current gformat is supported by the fire stick
    global input
    global reencodeVideo
    filename = os.path.join(input, file)
    s = check_output(['mediainfo', '--Inform=Video;%Format%', filename])  # Gets the output from mediainfo
    s1 = s[:-1]
    name = s1.decode("utf-8")  # s1 is a bytes object but we need a string for the check
    print("Video codec: {}".format(name))
    if name in supportedVideoCodecs:  # Is the video codec supported by the fire stick?
        print("Video codec looks fine")
        reencodeVideo = 0
    else:
        print("Video codec needs to be changed")
        reencodeVideo = 1
    checkAcodec(file)


def checkAcodec(file):  # Checks if the current gformat is supported by the fire stick
    global input
    global reencodeAudio
    filename = os.path.join(input, file)
    s = check_output(['mediainfo', '--Inform=Audio;%Format%', filename])  # Gets the output from mediainfo
    s1 = s[:-1]
    name = s1.decode("utf-8")  # s1 is a bytes object but we need a string for the check
    print("Audio codec: {}".format(name))
    if name in supportedAudioCodecs:  # Is the audio codec supported by the fire stick?
        print("Audio codec looks fine")
        reencodeAudio = 0
    else:
        print("Audio codec needs to be changed")
        reencodeAudio = 1
    reencode(file)


def reencode(file):
    global DEFAULT_GFORMAT
    global DEFAULT_VCODEC
    global DEFAULT_ACODEC
    global containerformat
    global input
    filename = os.path.join(input, file)

    Container = 0
    Video = 0
    Audio = 0

    if changeContainer:  # The container needs to be changed
        Container = DEFAULT_GFORMAT
    else:  # Container is already fine
        Container = "copy"

    if reencodeVideo:  # Video codec needs to be changed
        Video = DEFAULT_VCODEC
    else:  # Video codec is already fine
        Video = "copy"

    if reencodeAudio:  # Audio codec needs to be changed
        Audio = DEFAULT_ACODEC
    else:  # Audio codec is already fine
        Audio = "copy"

    if(Container == "copy" and Video == "copy" and Audio == "copy"):
        print("{}: File is already playable by the fire tv stick".format(file))
        print()
    else:  # File needs to be reencoded
        # name = os.path.splitext(file)[0]  # This removes the file extension from the name

        bakname = filename + ".bak"
        os.rename(filename, bakname)  # File needs to be renamed so it's not overwritten
        sourceFile = shlex.quote(bakname)
        outputFile = shlex.quote(filename)

        if(containerformat == "MPEG-4"):  # We only need to check for mp4 since if it's not mp4 it's either mkv or it's gonna be reencoded to mkv
            finalFile = outputFile + ".mp4"  # This is the new name for the output file
        else:
            finalFile = outputFile + ".mkv"  # This is the new name for the output file
        print("Reencoding file...")

        command = "ffmpeg -loglevel error -stats -i " + sourceFile + " -map 0 -scodec copy -vcodec " + Video + " -acodec " + Audio + " " + finalFile
        try:
            subprocess.call(command, shell=True)  # Run the command
        except OSError as e:  # Some error happened
            if e.errno == os.errno.ENOENT:  # ffmpeg is not installed
                print("ffmpeg does not seem to be installed. Please install it if you want to run this script")
            else:  # Something else went wrong
                raise
        print("The file has successfully been reencoded")
        print()


checkArguments()
