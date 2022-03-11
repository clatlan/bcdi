# -*- coding: utf-8 -*-

# BCDI: tools for pre(post)-processing Bragg coherent X-ray diffraction imaging data
#   (c) 07/2017-06/2019 : CNRS UMR 7344 IM2NP
#   (c) 07/2019-05/2021 : DESY PHOTON SCIENCE
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Module containing decorators and context manager classes for input-output."""

from functools import wraps
from typing import Callable, Optional, Union


class ContextFile:
    """Convenience context manager to open files."""

    def __init__(
        self,
        filename: str,
        open_func: Union[type, Callable],
        scan_number: Optional[int] = None,
        mode: str = "r",
        encoding: str = "utf-8",
    ):
        self.filename = filename
        self.file = None
        self.open_func = open_func
        self.scan_number = scan_number
        self.mode = mode
        self.encoding = encoding

    def __enter__(self):
        if (
            self.open_func.__module__ == "silx.io.specfile"
            and self.open_func.__name__ == "SpecFile"
        ):
            self.file = self.open_func(self.filename)
        elif self.open_func.__name__ == "open":
            self.file = self.open_func(
                self.filename, mode=self.mode, encoding=self.encoding
            )
        elif self.open_func.__name__ == "File":
            self.file = self.open_func(self.filename, mode=self.mode)
        else:
            raise NotImplementedError(f"open function {self.open_func} not supported")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False


def safeload(func):
    @wraps(func)
    def helper(self, *args, **kwargs):
        setup = kwargs.get("setup")
        if setup is None:
            raise ValueError
        if not isinstance(setup.logfile, ContextFile):
            raise TypeError(
                "setup.logfile should be a ContextFile, " f"got {type(setup.logfile)}"
            )
        with setup.logfile as file:
            return func(self, *args, file=file, **kwargs)

    return helper


def safeload_static(func):
    @wraps(func)
    def helper(*args, **kwargs):
        setup = kwargs.get("setup")
        if setup is None:
            raise ValueError
        if not isinstance(setup.logfile, ContextFile):
            raise TypeError(
                "setup.logfile should be a ContextFile, " f"got {type(setup.logfile)}"
            )
        with setup.logfile as file:
            return func(*args, file=file, **kwargs)

    return helper
