# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import flask
import gevent
import typing
import ruamel.yaml
import mimetypes

from bliss.config.conductor.client import get_default_connection
from .model import HomepageDesc


yaml_load = ruamel.yaml.YAML().load


def domain_name(request):
    """Return the fully qualified domain name"""
    try:
        host, _ = request.server
        return host
    except TypeError:
        return request.host.split(":")[0]


def create_app(log_viewer_port):
    app = flask.Flask(__name__)

    def read_config_file(name: str, default: typing.Any = None) -> typing.Any:
        beacon = get_default_connection()
        try:
            data = beacon.get_config_file(name)
            content = yaml_load(data)
            return content
        except RuntimeError:
            app.logger.info("Error while loading %s", name, exc_info=True)
            return default

    def load_resources():
        with gevent.Timeout(30, TimeoutError):
            app.logger.info("Loading beacon configuration ...")
            cfg = read_config_file("__init__.yml", {})
            homepage_cfg = read_config_file("services/homepage.yml", {})
            homepage_desc = HomepageDesc(**homepage_cfg)
            app.logger.info("Beacon configuration loaded")
        return cfg, homepage_desc

    cfg, homepage_desc = load_resources()

    @app.route("/")
    def index():
        # Reload the resources
        nonlocal cfg, homepage_desc
        cfg, homepage_desc = load_resources()
        institute = cfg.get("institute", cfg.get("synchrotron"))
        laboratory = cfg.get("laboratory", cfg.get("beamline"))
        full_name = " - ".join(filter(None, (institute, laboratory)))

        return flask.render_template(
            "index.html",
            name=full_name,
            beamline=cfg.get("beamline", "ESRF"),
            institute=institute,
            laboratory=laboratory,
            extra_links=homepage_desc.extra_links,
        )

    @app.route("/background.jpg")
    def background():
        if homepage_desc.background:
            mimetype = mimetypes.guess_type(homepage_desc.background)
            if mimetype[0] != "image/jpeg":
                raise ValueError(
                    f"Unexpected mimetype {mimetype[0]} for file {homepage_desc.background}"
                )
            return flask.send_file(homepage_desc.background, mimetype="image/jpeg")
        return flask.redirect(
            flask.url_for("static", filename="img/esrf-at-night.jpg"), 301
        )

    @app.route("/multivisor/")
    @app.route("/status/")
    def multivisor():
        return flask.redirect(f"http://{domain_name(flask.request)}:22000")

    @app.route("/supervisor/")
    def supervisor():
        return flask.redirect(f"http://{domain_name(flask.request)}:9001")

    @app.route("/log/")
    @app.route("/logs/")
    def log_viewer():
        return flask.redirect(f"http://{domain_name(flask.request)}:{log_viewer_port}")

    @app.route("/favicon.ico")
    def favicon():
        return flask.redirect(flask.url_for("static", filename="favicon.ico"), 301)

    return app
