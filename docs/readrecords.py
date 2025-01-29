import records
from sys import argv
from os import path

if __name__ == '__main__':
    # Without an input_stream the Wrye record classes are more or less unusable.
    input_file = open(argv[1], "rb")
    reader = records.Tes3Reader(path.basename(argv[1]), input_file)

    records = []
    while not reader.atEnd():
        (name, size, deleted_flag, frozen_flag) = reader.unpackRecHeader()
        header = (name, size, deleted_flag, frozen_flag)
        data = reader.read(size)

        # print(name, round(size / 1024))
        records.append((header, data))

    input_file.close()
