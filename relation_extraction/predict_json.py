import os
from relation_extraction.predict import predict
import time
import json
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from sklearn import metrics

from .data_utils import SentenceREDataset, get_idx2tag, load_checkpoint, save_checkpoint
from .model import SentenceRE

here = os.path.dirname(os.path.abspath(__file__))


def test_json(hparams):
    device = hparams.device
    seed = hparams.seed
    torch.manual_seed(seed)

    pretrained_model_path = hparams.pretrained_model_path
    test_file = hparams.test_file
    result_file = hparams.result_file
    tagset_file = hparams.tagset_file
    model_file = hparams.model_file

    max_len = hparams.max_len
    # train_dataset
    train_dataset = SentenceREDataset(test_file, tagset_path=tagset_file,
                                      pretrained_model_path=pretrained_model_path,
                                      max_len=max_len)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=False)

    # model
    idx2tag = get_idx2tag(tagset_file)
    hparams.tagset_size = len(idx2tag)
    model = SentenceRE(hparams).to(device)
    model.load_state_dict(torch.load(model_file))
    model.eval()

    predict_result = []
    for sample_batched in tqdm(train_loader, desc='Testing'):
        token_ids = sample_batched['token_ids'].to(device)
        token_type_ids = sample_batched['token_type_ids'].to(device)
        attention_mask = sample_batched['attention_mask'].to(device)
        e1_mask = sample_batched['e1_mask'].to(device)
        e2_mask = sample_batched['e2_mask'].to(device)
        model.zero_grad()
        logits = model(token_ids, token_type_ids, attention_mask, e1_mask, e2_mask)
        predict_result += [idx2tag[logit.argmax(0).item()] for logit in logits]
    out = open(result_file, 'w')
    with open(test_file, 'r') as raw:
        lines = raw.readlines()
        for i, line in enumerate(lines):
            j = json.loads(line)
            j['relation'] = predict_result[i]
            j = json.dumps(j, ensure_ascii=False)
            out.write(j + '\n')

    out.close()
