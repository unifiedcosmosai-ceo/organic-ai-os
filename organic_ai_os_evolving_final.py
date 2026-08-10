def parse_fasta(text):
    records = {}
    header = ""
    for line in text.split("\n"):
        if line.startswith(">"):
            header = line[1:]
            records[header] = ""
        else:
            records[header] += line
    return records
