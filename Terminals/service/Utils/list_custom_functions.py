def to_list(element) -> list:
    if hasattr(element, "__iter__"):
        res = element
    else:
        res = [element]
    return res


def Flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def sort_data_by_list(key_list, sorted_list):
    """
    sorted by list templates
    """
    sort_map = {key_name: next((idx for idx, val in enumerate(key_list) if val in key_name),
                               len(sorted_list)) for key_name in sorted_list}
    res = sorted(sorted_list, key=sort_map.__getitem__)
    return res


def get_sub_names_in_names(list_of_names, sublist):
    """
    list of names ["system_name","RE","HE1","CE1","HE2","CE2"]
    sublist df.columns
    out list of columns
    """
    df_short_column_all = [
        head for head in sublist
        for e_name in list_of_names
        if head is not None and e_name in head
    ]
    return df_short_column_all


def set_list(lst):
    setList = []
    for i in lst:
        if not i in setList:
            setList.append(i)
    return setList
