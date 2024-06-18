

def dict_merge(dict_1, dict_2):
    for k, v in dict_2.items():
        if k in dict_1 and isinstance(dict_1[k], dict) and isinstance(v, dict):
            dict_merge(dict_1[k], v)
        else:
            dict_1[k] = v
    return dict_1


