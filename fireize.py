#!/usr/bin/python3

import subprocess
import sys
import os

SUPPORTED_EXTENSIONS = 'mkv', 'avi', 'mp4', '3gp', 'mov', 'mpg', 'mpeg', 'qt', 'wmv', 'm2ts'

SUPPORTED_GFORMATS = "('MPEG-4' 'Matroska')"
UNSUPPORTED_GFORMATS = ('BDAV' 'AVI' 'Flash Video')

SUPPORTED_VCODECS = ('AVC')
UNSUPPORTED_VCODECS = ('MPEG-4 Visual' 'xvid' 'MPEG Video')

SUPPORTED_ACODECS = ('AAC' 'MPEG Audio' 'Vorbis' 'Ogg')
UNSUPPORTED_ACODECS = ('AC-3' 'DTS' 'PCM')

DEFAULT_VCODEC = "h264"
DEFAULT_ACODEC = "libvorbis"
DEFAULT_GFORMAT = "mp4"

changeContainer = 0
reencodeVideo = 0
reencodeAudio = 0

def checkArguments():  # This is used to test if the program was called with a file or directory argument
    array = sys.argv
    input = sys.argv[1]
    if len(array) > 2 or len(array) <= 1:  # Did the user enter the rigth amount of arguments?
        print("Please append exactly one file or directory to the program call")
    elif os.path.isfile(input):  # It's a file
        if input.endswith(tuple(SUPPORTED_EXTENSIONS)):  # Check to see if the file extension is supported
            checkGformat(input)
        else:
            print("This file type is not supported")
    elif os.path.isdir(input):  # It's a directory
        for file in os.listdir(input):  # We need to run the program on every single file inside that folder
            if file.endswith(tuple(SUPPORTED_EXTENSIONS)):
                checkGformat(file)
            else:
                print("{}: This file type is not supported".format(file))
    else:  # It's something else
        print("Unknown input, please append a file or directory to the program call")


def checkGformat(file):  # Checks if the current gformat is supported by the fire stick
    global changeContainer
    try:
        s = subprocess.Popen(['mediainfo', '--Inform=General;%Format%', file], stdout=subprocess.PIPE)  # Gets the output from mediainfo
    except OSError as e:  # Some error happened
        if e.errno == os.errno.ENOENT:  # mediainfo is not installed
            print("mediainfo does not seem to be installed. Please install it if you want to run this script")
        else:  # Something else went wrong
            raise
    print(s)
    name = s.stdout.readline().decode().strip()  # Strips the output to first line only so we can compare it with our list
    if not name:
        print("name ist leer")
    elif name in SUPPORTED_GFORMATS:  # Is the container supported by the fire stick?
        print("{}: Container looks fine".format(file))
        changeContainer = 0
    else:
        print("{}: Container needs to be changed".format(file))
        changeContainer = 1
    checkVcodec(file)

def checkVcodec(file):  # Checks if the current gformat is supported by the fire stick
    global reencodeVideo
    s = subprocess.Popen(['mediainfo', '--Inform=Video;%Format%', file], stdout=subprocess.PIPE)  # Gets the output from mediainfo
    name = s.stdout.readline().decode().strip()  # Strips the output to first line only so we can compare it with our list
    if name in SUPPORTED_VCODECS:  # Is the video codec supported by the fire stick?
        print("{}: Video codec looks fine".format(file))
        reencodeVideo = 0
    else:
        print("{}: Video codec needs to be changed".format(file))
        reencodeVideo = 1
    checkAcodec(file)


def checkAcodec(file):  # Checks if the current gformat is supported by the fire stick
    global reencodeAudio
    s = subprocess.Popen(['mediainfo', '--Inform=Audio;%Format%', file], stdout=subprocess.PIPE)  # Gets the output from mediainfo
    name = s.stdout.readline().decode().strip()  # Strips the output to first line only so we can compare it with our list
    if name in SUPPORTED_ACODECS:  # Is the audio codec supported by the fire stick?
        print("{}: Audio codec looks fine".format(file))
        reencodeAudio = 0
    else:
        print("{}: Audio codec needs to be changed".format(file))
        reencodeAudio = 1
    reencode(file)


def reencode(file):
    global DEFAULT_GFORMAT
    global DEFAULT_VCODEC
    global DEFAULT_ACODEC

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
        print("{}: File is playable by the fire tv stick".format(file))
        print()
    else:  # File needs to be reencoded
        name = os.path.splitext(file)[0]  # This removes the file extension from the name
        newName = name + ".mp4"  # This is the new name for the output file
        print("{}: Reencoding file...".format(file))
        os.rename(file, file + ".bak")  # File needs to be renamed so it's not overwritten
        command = "ffmpeg -loglevel error -stats -i " + file + ".bak" + " -map 0 -scodec copy -vcodec " + Video + " -acodec " + Audio + " " + newName
        try:
            subprocess.call(command, shell=True)  # Run the command
        except OSError as e:  # Some error happened
            if e.errno == os.errno.ENOENT:  # ffmpeg is not installed
                print("ffmpeg does not seem to be installed. Please install it if you want to run this script")
            else:  # Something else went wrong
                raise
        print()  # Just to make it look a little nicer


checkArguments()
