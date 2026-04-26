def parse_instruction(raw_str):
    det = raw_str.strip().split()
    op = det[0].upper()

    if op == "LW":
        return {
            "op": op,
            "dst": det[1].rstrip(","),
            "src": [det[2].split("(")[1][:-1]]  # extract R from 0(R)
        }
    elif op == "SW":
        return {
            "op": op,
            "dst": None,
            "src": [det[1].rstrip(","), det[2].split("(")[1][:-1]]
        }
    else:  # ADD, SUB
        return {
            "op": op,
            "dst": det[1].rstrip(","),
            "src": [det[2].rstrip(","), det[3].rstrip(",")]
        }

def parseAll(raw_list):
    return [parse_instruction(r) for r in raw_list]