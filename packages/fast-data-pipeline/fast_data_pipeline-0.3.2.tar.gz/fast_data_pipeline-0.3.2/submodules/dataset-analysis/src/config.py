from pathlib import Path

import plotly.graph_objects as go

LOGGING_DIR = Path("logs")

LOGGING_DIR.mkdir(exist_ok=True)
LOGGING_DIR.resolve(strict=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "detailed": {"format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "minimal",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "filename": str(LOGGING_DIR / "latest.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 31,
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

# Define LaTeX-style Plotly template
LATEX_TEMPLATE = go.layout.Template(
    layout={
        "font": {"family": "Latin Modern Roman, Computer Modern, serif", "size": 12, "color": "black"},
        "title": {"font": {"size": 14, "family": "Latin Modern Roman, Computer Modern, serif"}},
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "xaxis": {
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
            "showline": True,
            "linecolor": "black",
            "ticks": "outside",
            "tickcolor": "black",
            "title_font": {"size": 12, "family": "Latin Modern Roman, Computer Modern, serif"},
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "lightgray",
            "zeroline": False,
            "showline": True,
            "linecolor": "black",
            "ticks": "outside",
            "tickcolor": "black",
            "title_font": {"size": 12, "family": "Latin Modern Roman, Computer Modern, serif"},
        },
        "legend": {"bordercolor": "Black", "borderwidth": 0.5, "font": {"size": 11}},
        "margin": {"l": 60, "r": 40, "t": 40, "b": 50},
    }
)
