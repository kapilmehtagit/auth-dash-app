from typing import Any, Dict

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask.app import Flask

from src.DashApp import DashApp

MIN_HEIGHT = 200


class ExampleDashApp1(DashApp):
    def __init__(self, url_base: str, options: Dict) -> None:
        self.options = options
        super().__init__(url_base)

    def initialize(self, server: Flask) -> None:
        super().initialize(server)
        self.app.layout = self.onload

        @self.app.callback(
            Output(
                component_id=f'{self.options["name"]}_my_output',
                component_property="children",
            ),
            [
                Input(
                    component_id=f'{self.options["name"]}_my_input',
                    component_property="value",
                )
            ],
        )
        def update_output_div(input_value: str) -> str:
            return "Output: {}".format(input_value)

    def onload(self) -> Any:
        return dbc.Container(
            [
                html.H6("Change the value in the text box to see callbacks in action!"),
                html.Div(
                    [
                        "Input: ",
                        dcc.Input(
                            id=f'{self.options["name"]}_my_input',
                            value="initial value",
                            type="text",
                        ),
                    ]
                ),
                html.Br(),
                html.Div(id=f'{self.options["name"]}_my_output'),
            ]
        )
