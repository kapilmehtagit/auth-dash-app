from io import BytesIO
from typing import Any, Dict, Optional

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from azure.identity._credentials.default import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dash.dependencies import Input, Output
from flask.app import Flask

from src.DashApp import DashApp

MIN_HEIGHT = 600


class AzureDataExample(DashApp):
    df = None
    all_dims = ['sepal_length', 'sepal_width', 
    'petal_length', 'petal_width']

    def __init__(
        self, url_base: str, options: Dict, credential: Optional[DefaultAzureCredential]
    ) -> None:
        self.options = options
        self.credential = credential
        super().__init__(url_base)

    def initialize(self, server: Flask) -> None:
        super().initialize(server)
        client = BlobServiceClient(
            account_url=self.options["blob_storage"],
            credential=self.credential,
        )
        self.container = client.get_container_client(self.options["container_name"])
        # This function is called every time the view is loaded.
        # If you want to load the data only once at start-up, change app.layout to point to a
        # a static value instead (for example `self.app.layout = html.Div([])`)
        self.app.layout = self.onload

        @self.app.callback(
            Output("splom", "figure"), 
            [Input("dropdown", "value")])
        def update_bar_chart(dims):
            fig = px.scatter_matrix(
                self.df, dimensions=dims, color="species")
            return fig

    def onload(self) -> Any:
        # All views are loaded once at startup. An empty dataframe is created first time the function runs to ensure
        # that massive amounts of data is not loaded when the server starts.
        if self.df is None:
            self.df = pd.DataFrame({
                'sepal_length': [1, 2, 3],
                'sepal_width': [1, 2, 3], 
                'petal_length': [1, 2, 3],
                'petal_width': [1, 2, 3],
                "species": ["1", "2", "3"]
            })
        else:
            # Load data from a blob storage in Azure using managed identity
            self.df = pd.read_csv(
                BytesIO(self.container.download_blob(self.options["file_name"]).readall())
            )

        return html.Div([
            dcc.Dropdown(
                id="dropdown",
                options=[{"label": x, "value": x} 
                        for x in self.all_dims],
                value=self.all_dims[:2],
                multi=True
            ),
            dcc.Graph(id="splom"),
        ])
