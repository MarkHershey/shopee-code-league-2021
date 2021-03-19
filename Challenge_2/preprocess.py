import csv
from markkk.logger import logger

NUM_ROWS = 50


with open("data/train.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
    line_count = 0
    for row in csv_reader:

        if line_count >= NUM_ROWS:
            break

        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            # print(list(row))
            _id = row[0]
            _input = row[1]
            _output = row[2]
            print(f"IN  : {_input}\nOUT : {_output}\n")
            line_count += 1

    print(f"Processed {line_count} lines.")
