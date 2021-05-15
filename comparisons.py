def part_of_full(part, full, check_values=False):
    scalars = (str,int,float,bytes)
    if part == full:  # its the same, all good
        return True
    if part is ... or full is ...:
        return True
    elif isinstance(full, (dict,)):
        partkeys = set(part.keys())
        if set(full.keys()) >= partkeys:
            if check_values:
                return all(part_of_full(part[key], full[key], check_values=True) for key in partkeys)
            else:
                return True
        else:
            return False
    elif isinstance(full, (list, tuple)):
        return all(part_of_full(full, p) for p in part)
    elif part in scalars:
        return type(full) == part
    else:
        return False


def test_simple():
    full = dict(a='a', b='b', c=dict(d='d', e='e', f='f'))
    part = dict(c=dict(d='d', e='e'))
    assert part_of_full(part, full)

    part = dict(c=dict(d='d', e='f'))
    assert part_of_full(part, full)

    part = dict(c=dict(d='d', e='f'))
    assert part_of_full(part, full, True) is False


if __name__ == '__main__':
    test_simple()
