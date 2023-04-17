import argparse
import wave
import sys

if sys.platform == 'win32':
    import winsound

    def play_wav(path):
        winsound.PlaySound(path, winsound.SND_FILENAME)

else:
    import pyaudio

    def play_wav(path):
        CHUNK = 1024

        f = wave.open(path, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        data = f.readframes(CHUNK)
        while data:
            stream.write(data)
            data = f.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_index", default=0, type=int)
    parser.add_argument("--filelists", nargs="+", default=[])
    parser.add_argument("--start_from", type=str)

    args = parser.parse_args()

    if not args.filelists:
        print('no filelist, please use --filelists to specify it')
        exit(1)

    touched = False

    for filelist in args.filelists:
        with open(filelist, 'r', encoding='utf-8') as file:
            paths = [data[args.audio_index]
                     for data in map(lambda s: s.split('|'), file.readlines())]
            for p in paths:
                touched |= p == args.start_from
                if args.start_from and not touched:
                    continue
                print(p)
                play_wav(p)
