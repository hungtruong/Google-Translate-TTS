#!/usr/bin/python

import sys
import argparse
import re
import urllib, urllib2
import time
from collections import namedtuple


def split_text(input_text, max_length=100):
    """
    Try to split between sentences to avoid interruptions mid-sentence.
    Failing that, split between words.
    See split_text_rec
    """
    def split_text_rec(input_text, regexps, max_length=max_length):
        """
        Split a string into substrings which are at most max_length.
        Tries to make each substring as big as possible without exceeding
        max_length.
        Will use the first regexp in regexps to split the input into
        substrings.
        If it it impossible to make all the segments less or equal than
        max_length with a regexp then the next regexp in regexps will be used
        to split those into subsegments.
        If there are still substrings who are too big after all regexps have
        been used then the substrings, those will be split at max_length.

        Args:
            input_text: The text to split.
            regexps: A list of regexps.
                If you want the separator to be included in the substrings you
                can add parenthesis around the regular expression to create a
                group. Eg.: '[ab]' -> '([ab])'

        Returns:
            a list of strings of maximum max_length length.
        """
        if(len(input_text) <= max_length): return [input_text]

        #mistakenly passed a string instead of a list
        if isinstance(regexps, basestring): regexps = [regexps]
        regexp = regexps.pop(0) if regexps else '(.{%d})' % max_length

        text_list = re.split(regexp, input_text)
        combined_text = []
        #first segment could be >max_length
        combined_text.extend(split_text_rec(text_list.pop(0), regexps, max_length))
        for val in text_list:
            current = combined_text.pop()
            concat = current + val
            if(len(concat) <= max_length):
                combined_text.append(concat)
            else:
                combined_text.append(current)
                #val could be >max_length
                combined_text.extend(split_text_rec(val, regexps, max_length))
        return combined_text

    return split_text_rec(input_text.replace('\n', ''),
                          ['([\,|\.|;]+)', '( )'])


audio_args = namedtuple('audio_args',['language','output'])

def audio_extract(input_text='',args=None):
    # This accepts :
    #   a dict,
    #   an audio_args named tuple
    #   or arg parse object
    if args is None:
        args = audio_args(language='en',output=open('output.mp3', 'w'))
    if type(args) is dict:
        args = audio_args(
                    language=args.get('language','en'),
                    output=open(args.get('output','output.mp3'), 'w')
        )
    #process input_text into chunks
    #Google TTS only accepts up to (and including) 100 characters long texts.
    #Split the text in segments of maximum 100 characters long.
    combined_text = split_text(input_text)

    #download chunks and write them to the output file
    for idx, val in enumerate(combined_text):
        mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s&total=%s&idx=%s" % (
            args.language,
            urllib.quote(val),
            len(combined_text),
            idx)
        headers = {"Host": "translate.google.com",
                   "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
                                 "AppleWebKit/535.19 (KHTML, like Gecko) "
                                 "Chrome/18.0.1025.163 Safari/535.19"
        }
        req = urllib2.Request(mp3url, '', headers)
        sys.stdout.write('.')
        sys.stdout.flush()
        if len(val) > 0:
            try:
                response = urllib2.urlopen(req)
                args.output.write(response.read())
                time.sleep(.5)
            except urllib2.URLError as e:
                print ('%s' % e)
    args.output.close()
    print('Saved MP3 to %s' % args.output.name)


def text_to_speech_mp3_argparse():
    description = 'Google TTS Downloader.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog='tunnel snakes rule')
    parser.add_argument('-o', '--output',
                        action='store', nargs='?',
                        help='Filename to output audio to',
                        type=argparse.FileType('wb'), default='out.mp3')
    parser.add_argument('-l', '--language',
                        action='store',
                        nargs='?',
                        help='Language to output text to.', default='en')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file',
                       type=argparse.FileType('r'),
                       help='File to read text from.')
    group.add_argument('-s', '--string',
                       action='store',
                       nargs='+',
                       help='A string of text to convert to speech.')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()
    

if __name__ == "__main__":
    args = text_to_speech_mp3_argparse()
    if args.file:
        input_text = args.file.read()
    if args.string:
        input_text = ' '.join(map(str, args.string))
    audio_extract(input_text=input_text, args=args)
