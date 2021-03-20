import csv
import pickle
from typing import Dict, List

from markkk.logger import logger
from nltk.tokenize import word_tokenize

# from torchtext.legacy.datasets import Dataset
from torchtext.legacy.data.example import Example
from torchtext.legacy.data import BucketIterator, Field

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
SRC = Field(init_token="<sos>", eos_token="<eos>", lower=True)
# target
TRG = Field(init_token="<sos>", eos_token="<eos>", lower=True)


def build_examples() -> List[Example]:
    examples = []
    logger.debug("Building Examples form data/train.csv")
    with open("data/train.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')

        line_count = 0
        for row in csv_reader:

            if line_count == 0:
                # first row (header)
                pass
            else:

                _in = row[1]
                _out = row[2]
                _in_tokens = tokenize(_in)
                _out_tokens = tokenize(_out)
                datapoint = {"in": _in_tokens, "out": _out_tokens}
                fields = {"in": ("in", SRC), "out": ("out", TRG)}
                example = Example.fromdict(datapoint, fields)
                examples.append(example)
                print(example.__dict__)

            line_count += 1

        logger.debug(f"Processed {line_count} lines.")

    logger.debug(f"Produced {len(examples)} examples.")
    return examples


# class AddressDataset(Dataset):

if __name__ == "__main__":
    # build_vocab()
    # load_vocab()
    build_examples()
