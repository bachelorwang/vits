AUDIO_PATH = 'audio'

def get_all_list_path(args):
    return 'filelists/all_%s.txt' % args.model

def get_train_list_path(args):
    return 'filelists/train_%s.txt' % args.model

def get_val_list_path(args):
    return 'filelists/val_%s.txt' % args.model