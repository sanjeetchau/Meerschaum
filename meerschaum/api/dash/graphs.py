#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Functions for building graphs of pipes' data.
"""

from __future__ import annotations
from meerschaum.utils.typing import WebState, List
from meerschaum.api import debug
from meerschaum.utils.packages import attempt_import, import_dcc, import_html, import_pandas
import plotly.express as px
pd = import_pandas()
px = attempt_import('plotly.express', warn=False)
dbc = attempt_import('dash_bootstrap_components')
html, dcc = import_html(), import_dcc()

def get_graphs_cards(state: Optional[WebState]):
    from meerschaum.api.dash.pipes import pipes_from_state
    pipes = pipes_from_state(state, as_list=True)
    cards, alerts = [], []
    for pipe in pipes:
        dt_name, id_name = pipe.get_columns('datetime', 'id', error=False)
        val_name = pipe.get_val_column(debug=debug)
        if dt_name is not None and val_name is not None:
            df = pipe.get_backtrack_data(backtrack_minutes=(1440))
            fig_args = {
                'data_frame': df,
                'x': dt_name,
                'y': val_name,
                'line_group': id_name,
                'title': f"Recent Data for Pipe\n'{pipe}'"
            }
            try:
                fig = px.line(**fig_args)
                graph = dcc.Graph(figure=fig)
                body = graph
            except Exception as e:
                body = html.P(f"Unable to create graph for pipe '{pipe}'. Please check that the columns are correctly set.")
        else:
            body = html.H4(f"Missing columns for pipe '{pipe}'")
        card = dbc.Card([
            #  dbc.CardHeader(html.H4(str(pipe))),
            dbc.CardBody(body),
            #  dbc.CardFooter(),
        ])
        cards.append(card)

    return cards, alerts
