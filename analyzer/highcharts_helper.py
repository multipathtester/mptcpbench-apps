"""
    Helper functions to generate graphes with Highcharts
    https://api.highcharts.com/highcharts/
    https://github.com/highcharts/highcharts
"""


def line_chart_dict(title, data, xtitle="", xtype="linear", ytitle="", marker=True,
                    ytype="linear", tooltip_header=None, tooltip_point=None):
    library = {
        "chart": {
            "type": "spline",
            "zoomType": "xy",
        },
        "title": {
            "text": title,
        },
        "credits": "false",
        "series": data,
        "plotOptions": {
            "series": {
                "marker": {
                    "enabled": marker,
                }
            }
        },
        "xAxis": {
            "type": xtype,
            "title": {
                "text": xtitle,
            },
        },
        "yAxis": {
            "type": ytype,
            "title": {
                "text": ytitle,
            },
        },
    }

    if tooltip_header and tooltip_point:
        library["tooltip"] = {
            "headerFormat": tooltip_header,
            "pointFormat": tooltip_point,
            "shared": False,
        }

    return {
        "type": "line",
        "card_title": title,
        "library": library,
    }

def scatter_chart_dict(title, data, xtitle="", xtype="linear", ytitle="",
                       ytype="linear", tooltip_header=None, tooltip_point=None):
    line = {
        "type": 'line',
        "name": "identity",
        "data": [[1, 1], [1000000, 1000000]],
        "marker": {
            "enabled": "false"
        },
        "states": {
            "hover": {
                "lineWidth": 0
            }
        },
    }
    library = {
        "chart": {
            "type": "scatter",
            "zoomType": "xy",
        },
        "title": {
            "text": title,
        },
        "credits": "false",
        "series": data + [line],
        "xAxis": {
            "min": 10,
            "max": 500000,
            "gridLineWidth": 1,
            "type": xtype,
            "title": {
                "text": xtitle,
            },
        },
        "yAxis": {
            "min": 10,
            "max": 500000,
            "gridLineWidth": 1,
            "type": ytype,
            "title": {
                "text": ytitle,
            },
        },
    }

    if tooltip_header and tooltip_point:
        library["tooltip"] = {
            "headerFormat": tooltip_header,
            "pointFormat": tooltip_point,
            "shared": False,
        }

    return {
        "type": "line",
        "card_title": title,
        "library": library,
    }
