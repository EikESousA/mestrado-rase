from utils.screens.menu_text_line import menu_text_line


def menu_prompt(
    text: str,
    color: str | None = None,
    end: str | None = None,
    flush: bool | None = None,
) -> None:
    line = menu_text_line(text, align_left=True, color=color)
    kwargs = {}
    if end is not None:
        kwargs["end"] = end
    if flush is not None:
        kwargs["flush"] = flush
    print(line, **kwargs)
