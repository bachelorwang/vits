import argparse
import filelist
import os


def check_list(list_path, args):
    cleaned_list_path = list_path + '.' + args.cleaned_extension
    with open(list_path, 'r', encoding='utf-8') as list_file,\
            open(cleaned_list_path, 'r', encoding='utf-8') as cleaned_list_file:
        src_list = [s.split('|') for s in list_file.readlines()]
        cleaned_list = [s.split('|') for s in cleaned_list_file.readlines()]
        n = len(src_list)
        errors = []
        if n != len(cleaned_list):
            errors.append('length of lists are not matched: %d<>%d' %
                          (n, len(cleaned_list)))
            n = min(len(cleaned_list), n)
        for i in range(n):
            audio_path = src_list[i][args.audio_index]
            if audio_path != cleaned_list[i][args.audio_index]:
                errors.append('line %d audio path mismatched: %s<>%s' % (
                    audio_path, cleaned_list[i][args.audio_index]))
            if not os.path.isfile(audio_path):
                errors.append('audio path %s doesn\' exist' % audio_path)
            emopath = filelist.get_emo_filepath(audio_path)
            if not os.path.isfile(emopath):
                errors.append('emo path %s doesn\' exist' % emopath)
        return errors
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_index", default=0, type=int)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--cleaned_extension", type=str, default="cleaned")

    args = parser.parse_args()

    train_list_path = filelist.get_train_list_path(args)
    val_list_path = filelist.get_val_list_path(args)
    errors = []
    errors += check_list(train_list_path, args)
    errors += check_list(val_list_path, args)

    if errors:
        print(errors)
    else:
        print('passed')
    exit(len(errors))
