from typing import List

import msal
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from flask import Flask, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap

import config
from flask_session import Session
from src.auth import Auth, login_required
from src.DashApp import DashApp
from src.AzureDataExample import AzureDataExample
from src.ExampleDashApp1 import ExampleDashApp1
from src.ExampleDashApp2 import ExampleDashApp2

credential = DefaultAzureCredential(exclude_visual_studio_code_credential=True)
client = SecretClient(vault_url=config.KEYVAULT_URI, credential=credential)


app = Flask(__name__, template_folder="templates")
bootstrap = Bootstrap()
bootstrap.init_app(app)
app.config.from_object(config)
Session(app)

# Dash stuff
DASH_URL_BASE = "/dash/"

# Extend this list with more dash apps
dash_apps: List[DashApp] = [
    ExampleDashApp1(DASH_URL_BASE + "test1/", {"name": "Example Dash App 1"}),
    ExampleDashApp2(DASH_URL_BASE + "test2/", {"name": "Example Dash App 2"}),
    AzureDataExample(
        DASH_URL_BASE + "iris-data/",
        {
            "name": "Example Iris Data",
            "blob_storage": "https://{{ BLOB_STORAGE_NAME }}.blob.core.windows.net",
            "container_name": "{{ CONTAINER_NAME }}",
            "file_name": "iris.csv"
        },
        credential
    ),
]

auth = Auth(config, credential)

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

for i, dash_app in enumerate(dash_apps):
    dash_app.initialize(app)
    for view_func in dash_app.app.server.view_functions:
        dash_app.app.server.view_functions[view_func] = login_required(
            auth, config.ROLES, config.SCOPES
        )(dash_app.app.server.view_functions[view_func])


@app.route("/")
def index():
    auth_uri = ""
    if "flow" in session:
        auth_uri = session["flow"]["auth_uri"]
    name = ""
    if "user" in session:
        name = session["user"]["name"].split(" ")[0]
    return render_template(
        "index.html",
        auth_url=auth_uri,
        name=name,
    )


@app.route("/login")
def login():
    session["flow"] = auth._build_auth_code_flow(scopes=config.SCOPES)
    user = ""
    if "user" in session:
        user = session["user"]
    return render_template(
        "index.html",
        user=user,
        auth_url=session["flow"]["auth_uri"],
        version=msal.__version__,
    )


@app.route("/menu")
@login_required(auth, config.ROLES, config.SCOPES)
def menu():
    return render_template(
        "menu.html",
        name=session["user"]["name"],
        dash_apps=dash_apps,
    )


@app.route("/access_denied")
def access_denied():
    session["flow"] = auth._build_auth_code_flow(scopes=config.SCOPES)
    return render_template("access_denied.html", auth_url=session["flow"]["auth_uri"])


@app.route(
    config.REDIRECT_PATH
)
def authorized():
    try:
        cache = auth._load_cache()
        result = auth._build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        print(session["user"])
        print(result.get("id_token_claims"))
        auth._save_cache(cache)
    except ValueError:
        pass
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        config.AUTHORITY
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("index", _external=True)
    )


@app.route("/graphcall")
@login_required(auth, config.ROLES, config.SCOPES)
def graphcall():
    token = auth._get_token_from_cache(config.SCOPES)
    graph_data = requests.get(
        config.ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
    ).json()
    return render_template("display.html", result=graph_data)


app.jinja_env.globals.update(
    _build_auth_code_flow=auth._build_auth_code_flow
)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
