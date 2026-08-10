def parse_fasta(text):
    records = {}
    current_header = None
    current_seq_parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_header is not None:
                records[current_header] = ''.join(current_seq_parts)
            current_header = line[1:].split()[0]
            current_seq_parts = []
        else:
            current_seq_parts.append(line)
    if current_header is not None:
        records[current_header] = ''.join(current_seq_parts)
    return records