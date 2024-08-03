import dash
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_cytoscape as cyto
from utils import parse_nodes_and_edges as pne
from utils import parse_pipeline_text as pp
from utils import retrieve_pipeline_file as ret
import dash_bootstrap_components as dbc

cyto.load_extra_layouts()

app = Dash(
    'Bioinformatics_Pipeline_Viz',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server


# Parent container for the Menu (topmost section)
def return_menu():
    menu_div = html.Div(
        children=[
            return_dropdown()
        ],
        className='section',
        id='menu-container'
    )

    return menu_div


# Container for dropdown menu (located within Menu)
def return_dropdown():
    dropdown_menu_div = html.Div(
        children=[
            dcc.Dropdown(
                id='filename',
                options=[{'label': wf['name'], 'value': wf['file']} for wf in ret.get_pipeline_list()],
                placeholder='Select workflow',
            )
        ],
        id='dropdown-menu-container'
    )

    return dropdown_menu_div


# Parent container for the main content (i.e. Pipeline section)
def return_pipeline_content():
    pipeline_content_div = html.Div(
        children=[
            return_pipeline_diagram(),
            return_pipeline_overview()
        ],
        id='parent-pipeline-container'
    )

    return pipeline_content_div


# Parent container for cytoscape graph (located within Pipeline section)
def return_pipeline_diagram():
    pipeline_diagram_div = html.Div(
        cyto.Cytoscape(
            id='pipeline-viz-container',
            elements=[],
            layout=pne.define_cytoscape_layout(),
            style=pne.define_cytoscape_style(),
            stylesheet=pne.define_cytoscape_stylesheet()
        ),
        className='section',
        id='cytoscape-container'
    )

    return pipeline_diagram_div


# Parent container for pipeline + node details (located within Pipeline section)
def return_pipeline_overview():
    pipeline_overview_div = html.Div(
        children=[
            return_pipeline_desc(),
            return_node_desc()
        ],
        className='section',
        id='pipeline-overview-container'
    )

    return pipeline_overview_div


# Container for Pipeline description (located under Pipeline overview)
def return_pipeline_desc():
    pipeline_desc_div = html.Div(
        children=[
            html.H3(id='pipeline-overview-text'),
            html.P(id='pipeline-desc-text')
        ],
        id='pipeline-desc-container'
    )

    return pipeline_desc_div


# Container for Node details (located under Pipeline overview)
# Used for initialization of accordion elements
def return_node_desc():
    node_desc_div = html.Div(
        id='node-desc-container',
        children=[
            html.Div(
                children=[
                    dbc.Accordion(id='node-desc-accordion'),
                    dbc.Accordion(id='tool-output-inner-accordion')
                ]
            )
        ]
    )

    return node_desc_div


# Update cytoscape div and selected node when different dropdown item is selected
@callback(
    Output('pipeline-viz-container', 'elements'),
    Input('filename', 'value'),
)
def update_pipeline_content_div(pipeline_filename):
    if pipeline_filename is not None:
        cytoscape_elements = pne.generate_nodes(pipeline_filename) + pne.generate_edges(pipeline_filename)
        return cytoscape_elements
    else:
        return []


# Update workflow description when different dropdown filename is selected
@callback(
    Output('pipeline-overview-text', 'children'),
    Output('pipeline-desc-text', 'children'),
    Input('filename', 'value')
)
def update_pipeline_overview_div(filename):
    if filename is not None:
        workflow_name, workflow_desc = pp.get_workflow_details_from_filename(filename)

        return workflow_name, workflow_desc
    else:
        return [], []


# Callback for when a node is selected/unselected
@callback(
    Output('node-desc-container', 'children'),
    Output('tool-output-inner-accordion', 'active_item'),
    Output('node-desc-accordion', 'active_item'),
    Input('pipeline-viz-container', 'tapNodeData'),
    Input('pipeline-viz-container', 'selectedNodeData'),
    State('filename', 'value')
)
def update_node_desc_div(tapped_node, selected_node, filename):
    if selected_node:
        # If external node
        if '0.ext_data' in tapped_node['id']:
            return (
                pp.generate_external_node_accordion(tapped_node, filename),
                None,
                tapped_node['id']
            )
        # If internal node
        else:
            if 'parent' not in tapped_node.keys():
                return (
                    pp.generate_internal_node_desc_accordion(tapped_node),
                    dash.no_update,
                    tapped_node['id']
                )
            else:
                return (
                    pp.generate_internal_node_desc_accordion(tapped_node),
                    tapped_node['id'],
                    'tool-output'
                )
    # If no node is selected or node has no associated entry in xml
    # (selected_node is None) or (pp.generate_node_desc_accordion(selected_node) is None):
    else:
        return (
            return_node_desc().children,
            None,
            None
        )


app.layout = html.Div(
    children=[
        return_menu(),
        return_pipeline_content()
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
