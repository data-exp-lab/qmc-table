import json

import requests
from bokeh.embed import json_item
from bokeh.models import ColorBar, ColumnDataSource, CustomJS, HoverTool
from bokeh.palettes import Viridis256
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import linear_cmap
from flask import Flask, send_from_directory
from jinja2 import Template

app = Flask(__name__)

page = Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, shrink-to-fit=no, initial-scale=1">
  <meta name="description" content="QMC-HAMM Table">
  <meta name="author" content="Xarthisius">
  <title>QMC-HAMM Table</title>
  <!-- Custom CSS -->
  <link href="css/qmc.css" rel="stylesheet">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/css/dataTables.bootstrap.min.css">
  <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <script src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js"></script>
  <script src="https://cdn.datatables.net/1.11.3/js/dataTables.bootstrap.min.js"></script>
  <script src="https://kit.fontawesome.com/36ad4f215e.js" crossorigin="anonymous"></script>
  {{ resources }}
</head>

<body>
  {{body}}
  {{main_js}}
  <script>
  fetch('/plot')
    .then(function(response) { return response.json(); })
    .then(function(item) { return Bokeh.embed.embed_item(item); })
  </script>
</body>
</html>
"""
)


@app.route("/")
def root():
    with open("body.html", "r") as fp:
        body = fp.read()
    with open("main.js", "r") as fp:
        main_js = fp.read()
    return page.render(resources=CDN.render(), body=body, main_js=main_js)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


@app.route("/plot")
def plot():
    r = requests.get("https://girder.hub.yt/api/v1/qmc/count")
    T, P, count = zip(
        *[(_["_id"]["tkelvin"], _["_id"]["pgpa"], _["count"]) for _ in r.json()]
    )
    source = ColumnDataSource(data={"T": T, "P": P, "count": count})
    mapper = linear_cmap(
        field_name="count", palette=Viridis256, low=min(count), high=max(count)
    )
    p = figure(
        sizing_mode="stretch_width",
        toolbar_location="below",
        tools="box_select, pan, reset",
        active_drag="box_select",
    )
    p.add_tools(
        HoverTool(
            tooltips=[
                ("Temp [K]", "@T"),
                ("Pres [GPa]", "@P"),
                ("No. configs", "@count"),
            ]
        )
    )
    p.circle(y="T", x="P", size=15, source=source, line_color=mapper, color=mapper)
    p.yaxis[0].axis_label = "Temperature (K)"
    p.xaxis[0].axis_label = "Pressure (GPa)"

    color_bar = ColorBar(color_mapper=mapper["transform"], width=8)
    p.add_layout(color_bar, "right")

    source.selected.js_on_change(
        "indices",
        CustomJS(
            args=dict(source=source),
            code="""
            const inds = cb_obj.indices;
            const T = source.data['T'];
            const P = source.data['P'];
            var Pmin = 10000;
            var Tmin = 10000;
            var Tmax = 0;
            var Pmax = 0;
            for (let i = 0; i < inds.length; i++) {
                Pmin = Math.min(Pmin, P[inds[i]]);
                Tmin = Math.min(Tmin, T[inds[i]]);
                Pmax = Math.max(Pmax, P[inds[i]]);
                Tmax = Math.max(Tmax, T[inds[i]]);
            }
            if (Tmin > Tmax) {
                $('#Tmin').val(0);
                $('#Tmax').val(10000);
            } else {
                $('#Tmin').val(Tmin);
                $('#Tmax').val(Tmax);
            }
            if (Pmin > Pmax) {
                $('#Pmin').val(0);
                $('#Pmax').val(10000);
            } else {
                $('#Pmin').val(Pmin);
                $('#Pmax').val(Pmax);
            }
            $('#Pmax').change();
            """,
        ),
    )

    return json.dumps(json_item(p, "myplot"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
