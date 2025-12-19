"""Kryten Bingo Service - Chat moderation and filtering."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("kryten-bingo")
except PackageNotFoundError:
    __version__ = "0.0.0"
