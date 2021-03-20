import csv
import pickle
from typing import Dict, List

import torch
import torchtext.legacy.data as torchtextdata
from markkk.logger import logger
from nltk.tokenize import word_tokenize
from torchtext.legacy.data import BucketIterator, Field
from torchtext.legacy.data.dataset import Dataset
from torchtext.legacy.data.example import Example

NUM_ROWS = 50


# with open("data/train.csv") as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
#     line_count = 0
#     for row in csv_reader:

#         if line_count >= NUM_ROWS:
#             break

#         if line_count == 0:
#             print(f'Column names are {", ".join(row)}')
#             line_count += 1
#         else:
#             # print(list(row))
#             _id = row[0]
#             _input = row[1]
#             _output = row[2]
#             print(f"IN  : {_input}\nOUT : {_output}\n")
#             line_count += 1

#     print(f"Processed {line_count} lines.")


def build_vocab():
    vocab = {}

    logger.debug("Reading data/train.csv")
    with open("data/train.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')

        line_count = 0
        for row in csv_reader:

            if line_count == 0:
                # first row (header)
                line_count += 1
            else:
                _input = row[1]
                _output = row[2]
                info = tokenize(_input) + tokenize(_output)
                # print(info)
                for token in info:
                    if token in vocab:
                        vocab[token] += 1
                    else:
                        vocab[token] = 1
                line_count += 1

        logger.debug(f"Processed {line_count} lines.")
        # logger.debug(f"Processed {len(vocab)} unique tokens.")

    logger.debug("Reading data/test.csv")
    with open("data/test.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')

        line_count = 0
        for row in csv_reader:

            if line_count == 0:
                # first row (header)
                line_count += 1
            else:
                _input = row[1]
                info = tokenize(_input)
                # print(info)
                for token in info:
                    if token in vocab:
                        vocab[token] += 1
                    else:
                        vocab[token] = 1
                line_count += 1

        logger.debug(f"Processed {line_count} lines.")

    # save vocab
    logger.debug(f"Processed {len(vocab)} unique tokens.")
    vocabfile = open("addr_vocab.pt", "wb+")
    pickle.dump(vocab, vocabfile)
    vocabfile.close()


def load_vocab():
    vocabfile = open("addr_vocab.pt", "rb")
    vocab = pickle.load(vocabfile)
    logger.debug(f"Loaded {len(vocab)} unique tokens.")
    # for keys in vocab:
    #     print(keys, "=>", vocab[keys])
    vocabfile.close()


def tokenize(string: str) -> List[str]:
    tokens = list(word_tokenize(string.lower()))
    new_tokens = []
    for token in tokens:
        if "/" not in token:
            new_tokens.append(token)
        else:
            if token.startswith("/"):
                new_tokens.append("/")
                new_tokens.append(token[1:])
            elif token[-1] == "/":
                new_tokens.append(token[:-1])
                new_tokens.append("/")
            else:
                idx = token.find("/")
                new_tokens.append(token[:idx])
                new_tokens.append(token[idx + 1 :])

    return new_tokens


# source
SRC = Field(tokenize=tokenize, init_token="<sos>", eos_token="<eos>", lower=True)
# target
TRG = Field(tokenize=tokenize, init_token="<sos>", eos_token="<eos>", lower=True)
BATCH_SIZE = 128
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_examples(exp: bool = False) -> List[Example]:
    NUM_ROWS = 50 if exp else 500001
    examples = []
    logger.debug("Building Examples form data/train.csv")
    with open("data/train.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')

        line_count = 0
        for row in csv_reader:

            if line_count >= NUM_ROWS:
                break

            if line_count == 0:
                # first row (header)
                pass
            else:

                _in = row[1]
                _out = row[2]
                # _in_tokens = tokenize(_in)
                # _out_tokens = tokenize(_out)
                datapoint = {"src": _in, "trg": _out}
                fields = {"src": ("src", SRC), "trg": ("trg", TRG)}
                example = Example.fromdict(datapoint, fields)
                examples.append(example)
                # print(example.__dict__)

            line_count += 1

        logger.debug(f"Processed {line_count} lines.")

    logger.debug(f"Produced {len(examples)} examples.")
    return examples


def get_iterators():
    def sort_key(ex):
        return torchtextdata.interleave_keys(len(ex.src), len(ex.trg))

    examples: List[Example] = build_examples(exp=False)
    fields: List[tuple] = [("src", SRC), ("trg", TRG)]
    dataset = Dataset(examples=examples, fields=fields)
    dataset.sort_key = sort_key
    train_ratio, test_ratio, validate_ratio = (0.7, 0.2, 0.1)
    train_data, valid_data, test_data = dataset.split(
        split_ratio=[train_ratio, test_ratio, validate_ratio]
    )

    logger.debug(f"Number of training examples: {len(train_data.examples)}")
    logger.debug(f"Number of validation examples: {len(valid_data.examples)}")
    logger.debug(f"Number of testing examples: {len(test_data.examples)}")

    SRC.build_vocab(train_data, min_freq=1)
    TRG.build_vocab(train_data, min_freq=1)

    train_iterator, valid_iterator, test_iterator = BucketIterator.splits(
        datasets=(train_data, valid_data, test_data),
        batch_size=BATCH_SIZE,
        device=device,
    )

    return train_iterator, valid_iterator, test_iterator


# class AddressDataset(Dataset):

if __name__ == "__main__":
    # build_vocab()
    # load_vocab()
    get_iterators()
