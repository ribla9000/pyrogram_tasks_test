def keyboard_cols(buttons, cols) -> list[list[object]]:
    menu = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
    return menu


def get_values(values) -> list[dict] | dict | None:
    if values is None:
        return None
    return [dict(value) for value in values] if isinstance(values, list) else dict(values)


def lengthen_text(text: str) -> str:
    default = 36
    fields = text.split("\n")
    length = len(fields[0])
    result = text

    if length < default:
        result = text + "ㅤ" * (default - length)

    return result


