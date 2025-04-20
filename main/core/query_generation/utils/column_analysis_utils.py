def get_groupable_column(columns, table, selector: int = 0):
    groupables = [col for col in columns if col not in table.primary_key.columns]
    if not groupables:
        return None
    return groupables[selector % len(groupables)]


def get_aggregatable_column(columns, selector: int = 0):
    aggregatables = []
    for col in columns:
        if hasattr(col.type, "python_type"):
            try:
                if issubclass(col.type.python_type, (int, float)):
                    aggregatables.append(col)
            except NotImplementedError:
                continue
    if not aggregatables:
        return None
    return aggregatables[selector % len(aggregatables)]


def get_filterable_column(table, selector: int = 0):
    filterables = []
    for col in table.columns:
        if hasattr(col.type, "python_type"):
            try:
                if col.type.python_type in (int, float, str):
                    filterables.append(col)
            except NotImplementedError:
                continue
    if not filterables:
        return None
    return filterables[selector % len(filterables)]


def generate_condition(column, selector=0):
    try:
        py_type = column.type.python_type
    except NotImplementedError:
        return "= 1"

    offset = sum(ord(c) for c in column.name) + selector

    if py_type == int:
        return f"> {offset % 10}"
    elif py_type == float:
        return f"> {round((offset % 10) + 0.5, 2)}"
    elif py_type == str:
        return f"LIKE '%a%'"
    else:
        return "= 1"
