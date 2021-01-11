import csv
from json import dumps as repr

with open("../mathics-development-guide/resources/named-characters-data.csv", "r") as i:
    reader = csv.reader(i, delimiter=",", escapechar="|")
    next(reader)

    inputrc = {}

    for row in reader:
        named_char, _, _, _, _, esc = row

        if esc:
            if esc in inputrc:
                raise ValueError(f"{esc}: {named_char} x {inputrc[esc]}")

            inputrc[esc] = named_char
            print(f"{repr(esc)}: {repr(named_char)}")

