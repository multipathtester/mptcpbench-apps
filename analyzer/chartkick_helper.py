"""
    Helper functions to generate graphes with Chartkick
    https://github.com/ankane/chartkick.js
"""


def bar_chart_dict(title, data, xtitle=None, ytitle=None):
    chart_dict = {
        "card_title": title,
        "type": "bar",
        "data": data,
    }
    library = {}
    if xtitle:
        library["xtitle"] = xtitle

    if ytitle:
        library["ytitle"] = ytitle

    chart_dict["library"] = library
    return chart_dict


def line_chart_dict(title, data, xtitle=None, ytitle=None):
    chart_dict = {
        "card_title": title,
        "type": "line-chartkick",
        "data": data,
    }
    library = {}
    if xtitle:
        library["xtitle"] = xtitle

    if ytitle:
        library["ytitle"] = ytitle

    chart_dict["library"] = library
    return chart_dict

def scatter_chart_dict(title, data, xtitle=None, ytitle=None):
    chart_dict = {
        "card_title": title,
        "type": "scatter-chartkick",
        "data": data,
    }
    library = {}
    if xtitle:
        library["xtitle"] = xtitle

    if ytitle:
        library["ytitle"] = ytitle

    chart_dict["library"] = library
    return chart_dict
