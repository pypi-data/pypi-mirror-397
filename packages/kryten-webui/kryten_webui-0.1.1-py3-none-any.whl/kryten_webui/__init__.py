"""Kryten WebUI Service - Web dashboard for Kryten ecosystem."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("kryten-webui")
except PackageNotFoundError:
    __version__ = "0.0.0"
