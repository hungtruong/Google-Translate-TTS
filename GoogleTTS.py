#!/usr/bin/python

import sys
import argparse
import re
import urllib, urllib2
import time
def main():
    description='Google TTS Downloader.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog='tunnel snakes rule')

    parser.add_argument('-o','--output',action='store',nargs='?',
                        help='Filename to output audio to',
                        type=argparse.FileType('w'), default='out.mp3')
    parser.add_argument('-l','--language', action='store', nargs='?',help='Language to output text to.',default='en')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f','--file',type=argparse.FileType('r'),help='File to read text from.')
    group.add_argument('-s', '--string',action='store',nargs='+',help='A string of text to convert to speech.')

    if len(sys.argv)==1:
       parser.print_help()
       sys.exit(1)

    args = parser.parse_args()
    if args.file:
        text = args.file.read()
    if args.string:
        text = ' '.join(map(str,args.string))

    #process text into chunks
    text = text.replace('\n','')
    text_list = re.split('(\,|\.)', text)
    combined_text = []
    for idx, val in enumerate(text_list):
        if idx % 2 == 0:
            combined_text.append(val)
        else:
            joined_text = ''.join((combined_text.pop(),val))
            if len(joined_text) < 100:
                combined_text.append(joined_text)
            else:
                subparts = re.split('( )', joined_text)
                temp_string = ""
                temp_array = []
                for part in subparts:
                    temp_string = temp_string + part
                    if len(temp_string) > 80:
                        temp_array.append(temp_string)
                        temp_string = ""
                #append final part
                temp_array.append(temp_string)
                combined_text.extend(temp_array)
    #download chunks and write them to the output file
    for idx, val in enumerate(combined_text):
        mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s&total=%s&idx=%s" % (args.language, urllib.quote(val), len(combined_text), idx)
        headers = {"Host":"translate.google.com",
          "Referer":"http://www.gstatic.com/translate/sound_player2.swf",
          "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
        req = urllib2.Request(mp3url, '', headers)
        sys.stdout.write('.')
        sys.stdout.flush()
        if len(val) > 0:
            try:
                response = urllib2.urlopen(req)
                args.output.write(response.read())
                time.sleep(.5)
            except urllib2.HTTPError as e:
                print ('%s' % e)
    args.output.close()

    print('Saved MP3 to %s' % args.output.name)

if __name__ == "__main__":
    main()
