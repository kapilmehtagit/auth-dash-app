import abc
from typing import Any

import dash
import dash_bootstrap_components as dbc
from flask import Flask


class DashApp(metaclass=abc.ABCMeta):
    def __init__(self, url_base: str) -> None:
        self.url_base = url_base
        self.app = None

    def initialize(self, server: Flask) -> None:
        FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
        external_stylesheets = [
            FA,
            dbc.themes.BOOTSTRAP,
        ]
        self.app = dash.Dash(
            server=server,
            url_base_pathname=self.url_base,
            suppress_callback_exceptions=True,
            external_stylesheets=external_stylesheets,
        )

    @abc.abstractmethod
    def onload(self) -> Any:
        pass
