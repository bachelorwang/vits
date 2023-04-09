import os
import argparse
import whisper
import common

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, required=True)
parser.add_argument("--lang", type=str, required=True)

args = parser.parse_args()
model = whisper.load_model("large")

def process(file):
    options = whisper.DecodingOptions(language=args.lang, without_timestamps=True)
    for _, _, filenames in os.walk(common.AUDIO_PATH):
        for filename in filenames:
            if not filename.endswith('.wav'):
                continue
            path = common.AUDIO_PATH + '/' + filename
            print('processing %s' % path)
            audio = whisper.load_audio(path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            result = whisper.decode(model, mel, options)
            file.write('%s|%s\n' % (path, result.text))
            file.flush()


all_list_path = common.get_all_list_path(args)
with open(all_list_path, 'w', encoding='utf-8') as file:
    process(file)
