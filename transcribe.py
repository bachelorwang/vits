import os
import argparse
import whisper
import filelist
import re

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, required=True)
parser.add_argument("--lang", type=str, required=True)
parser.add_argument("--pattern", type=str)

args = parser.parse_args()
model = whisper.load_model("large")
regex = None
if args.pattern:
    regex = re.compile(args.pattern)

def process(file):
    options = whisper.DecodingOptions(language=args.lang, without_timestamps=True)
    for _, _, filenames in os.walk(filelist.AUDIO_PATH):
        for filename in filenames:
            if not filename.endswith('.wav') or (regex and not regex.match(filename)):
                continue
            path = filelist.AUDIO_PATH + '/' + filename
            print('processing %s' % path)
            audio = whisper.load_audio(path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            result = whisper.decode(model, mel, options)
            file.write('%s|%s\n' % (path, result.text))
            file.flush()

all_list_path = filelist.get_all_list_path(args)
with open(all_list_path, 'w', encoding='utf-8') as file:
    process(file)
