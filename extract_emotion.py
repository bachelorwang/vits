# ref https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim

import argparse
import numpy as np
import torch
import torch.nn as nn
import librosa
import filelist
from transformers import Wav2Vec2Processor
from transformers.models.wav2vec2.modeling_wav2vec2 import (
    Wav2Vec2Model,
    Wav2Vec2PreTrainedModel,
)


class RegressionHead(nn.Module):
    r"""Classification head."""

    def __init__(self, config):

        super().__init__()

        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.final_dropout)
        self.out_proj = nn.Linear(config.hidden_size, config.num_labels)

    def forward(self, features, **kwargs):

        x = features
        x = self.dropout(x)
        x = self.dense(x)
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)

        return x


class EmotionModel(Wav2Vec2PreTrainedModel):
    r"""Speech emotion classifier."""

    def __init__(self, config):

        super().__init__(config)

        self.config = config
        self.wav2vec2 = Wav2Vec2Model(config)
        self.classifier = RegressionHead(config)
        self.init_weights()

    def forward(self, input_values):

        outputs = self.wav2vec2(input_values)
        hidden_states = outputs[0]
        hidden_states = torch.mean(hidden_states, dim=1)
        logits = self.classifier(hidden_states)

        return hidden_states, logits


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = 'audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim'
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = EmotionModel.from_pretrained(model_name).to(device)

print('device: %s' % device)


def process_func(
    x: np.ndarray,
    sampling_rate: int,
    embeddings: bool = False,
) -> np.ndarray:
    r"""Predict emotions or extract embeddings from raw audio signal."""

    # run through processor to normalize signal
    # always returns a batch, so we just get the first entry
    # then we put it on the device
    y = processor(x, sampling_rate=sampling_rate)
    y = y['input_values'][0]
    y = torch.from_numpy(y).to(device)

    # run through model
    with torch.no_grad():
        y = model(y)[0 if embeddings else 1]

    # convert to numpy
    y = y.detach().cpu().numpy()

    return y


def extract(path):
    print(path)
    wav, sr = librosa.load(path, sr=16000)
    emb = process_func(np.expand_dims(wav, 0), sr, embeddings=True)
    np.save(filelist.get_emo_filepath(path), emb.squeeze(0))
    return emb


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_index", default=0, type=int)
    parser.add_argument("--filelists", nargs="+", default=[])

    args = parser.parse_args()
    if not args.filelists:
        print('no filelist, please use --filelists to specify it')
        exit(1)

    for filelist in args.filelists:
        with open(filelist, 'r', encoding='utf-8') as file:
            paths = [data[args.audio_index]
                     for data in map(lambda s: s.split('|'), file.readlines())]
            for p in paths:
                extract(p)
