# -*- coding: UTF-8 -*-


import logging

from traceback import format_exc


_traceback_duplicated_ctx = dict()


def _duplicated(t: str, duplimit: int = 0) -> bool:
    h = hash(t)
    if h in _traceback_duplicated_ctx:
        _traceback_duplicated_ctx[h] += 1
    else:
        _traceback_duplicated_ctx[h] = 1
    if duplimit <= 0:
        return False
    if _traceback_duplicated_ctx[h] > duplimit:
        return True
    return False

def tracebackonce(msg = None) -> None:
    traceback(msg, duplimit=1)

def traceback(msg = None, duplimit: int = 0) -> None:
    try:
        _exc = format_exc()
    except Exception as e:
        logging.error(f"Not supported context for traceback.")
        tracebackonce(f"{e}")
        _exc = None

    if _duplicated(_exc, duplimit):
        return

    if msg is not None:
        logging.debug(msg)

    if _exc is not None:
        logging.debug(_exc)

