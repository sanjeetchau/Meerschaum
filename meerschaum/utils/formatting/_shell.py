#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Formatting functions for the interactive shell
"""

def make_header(
        message : str,
        ruler : str = '─',
    ) -> str:
    """Format a message string with a ruler.
    Length of the ruler is the length of the longest word
    
    Example:
        'My\nheader' -> 'My\nheader\n──────'

    Parameters
    ----------
    message : str :
        
    ruler : str :
         (Default value = '─')

    Returns
    -------

    """

    from meerschaum.utils.formatting import ANSI, UNICODE, colored
    if not UNICODE:
        ruler = '-'
    words = message.split('\n')
    max_length = 0
    for w in words:
        length = len(w)
        if length > max_length:
            max_length = length

    s = message + "\n"
    for i in range(max_length):
        s += ruler
    return s

def clear_screen(debug: bool = False) -> bool:
    """Clear the terminal window of all text. If ANSI is enabled,
    print the ANSI code for clearing. Otherwise, execute `clear` or `cls`.

    Parameters
    ----------
    debug: bool :
         (Default value = False)

    Returns
    -------

    """
    from meerschaum.utils.formatting import ANSI, get_console
    from meerschaum.utils.debug import dprint
    from meerschaum.config import get_config
    if not get_config('shell', 'clear_screen'):
        return True
    print("", end="", flush=True)
    if debug:
        dprint("Skipping screen clear.")
        return True
    if ANSI:
        if get_console() is not None:
            get_console().clear()
            print("", end="", flush=True)
            return True
        clear_string, reset_string = '\033c', '\033[0m'
        print(clear_string + reset_string, end="")
        print("", end="", flush=True)
        return True
    ### ANSI support is disabled, try system level instead
    import platform, subprocess
    command = 'clear' if platform.system() != "Windows" else "cls"
    rc = subprocess.call(command, shell=False)
    return rc == 0


def flush_with_newlines(debug: bool = False) -> None:
    """Print newlines such that the entire terminal is cleared and new text will show up at the bottom.

    Parameters
    ----------
    debug: bool :
         (Default value = False)

    Returns
    -------

    """
    import sys
    from meerschaum.utils.misc import get_cols_lines
    from meerschaum.utils.debug import dprint
    if debug:
        dprint("Skipping screen clear.")
        return
    cols, lines = get_cols_lines()
    sys.stderr.write('\n' * lines)


def progress(transient: bool = True, **kw):
    """

    Parameters
    ----------
    transient: bool :
         (Default value = True)
    **kw :
        

    Returns
    -------
    type
        

    """
    from meerschaum.utils.packages import import_rich, attempt_import
    rich = import_rich()
    rich_progress = attempt_import('rich.progress')
    return rich_progress.Progress(
        rich_progress.TextColumn(''),
        rich_progress.SpinnerColumn('clock'),
        rich_progress.TimeElapsedColumn(),
        rich_progress.TextColumn(''),
        rich_progress.BarColumn(bar_width=None,),
        transient = transient,
        **kw
    )

def live(**kw):
    """

    Parameters
    ----------
    **kw :
        

    Returns
    -------
    type
        

    """
    from meerschaum.utils.packages import import_rich, attempt_import
    rich = import_rich()
    rich_live = attempt_import('rich.live')
    return rich_live.Live(**kw)

