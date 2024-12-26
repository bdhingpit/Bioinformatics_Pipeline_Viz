import xml.etree.ElementTree as ET
import os
import dash_bootstrap_components as dbc
from dash import Dash, html
from utils import parse_nodes_and_edges as pne

utils_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_list_filepath = os.path.join(utils_dir, '..', 'pipeline', 'pipeline_list.xml')

pipeline_tree = ET.parse(pipeline_list_filepath)
pipeline_root = pipeline_tree.getroot()

tools_list_filepath = os.path.join(utils_dir, '..', 'pipeline', 'tools_list2.xml')
tools_tree = ET.parse(tools_list_filepath)
tools_root = tools_tree.getroot()


def get_workflow_details_from_filename(filename):
    """
    Get workflow name and description from the file associated
    with the selected pipeline.
    """
    if filename is not None:
        for parent in pipeline_root.findall('workflow'):
            for child in parent:
                if child.text == filename:
                    workflow_name = parent.attrib['name']
                    workflow_desc = parent.find('workflow-desc').text

                    return workflow_name, workflow_desc
    else:
        return None


"""
There are three types of nodes:
(1) Node referring to externally generated files. Labeled: "0.ext_data.*"
(2) Parent nodes or tools used in the pipeline
(3) Children nodes or outputs of tools used in the pipeline
From hereon, node types (2) and (3) will be called "internal nodes"
and node type (1) will be called "external node"
"""


def get_internal_node_desc(node):
    """
    Get details for selected internal node.
    """
    # Get tool name
    if 'label' in node.keys():  # If parent node is clicked
        tool_name = node['label']
    else:  # If internal node is clicked
        tool_name = node['parent'].split('.', maxsplit=1)[1]

    for tool in tools_root.iter('tool'):
        # If tool
        if tool.get('name') == tool_name:
            tool_desc = tool.find('desc').text
            tool_outputs = tool.findall('output')
            out_type = []
            out_desc = []

            for tool_out in tool_outputs:
                out_type.append(tool_out.find('output-type').text)
                out_desc.append(tool_out.find('output-desc').text)

            if 'parent' not in node.keys():
                return (
                    node['id'],
                    tool.get('name'),
                    tool_desc,
                    out_type,
                    out_desc
                )
            else:
                return (
                    node['parent'],
                    tool.get('name'),
                    tool_desc,
                    out_type,
                    out_desc
                )

    return None


def generate_internal_node_desc_accordion(node):
    """
    Create an accordion element for the selected internal node.
    """
    tool_id, tool_name, tool_desc, out_type_list, out_desc_list = get_internal_node_desc(node)

    accordion_div = html.Div(
        dbc.Accordion(
            id='node-desc-accordion',
            children=[
                dbc.AccordionItem(
                    item_id=tool_id,
                    children=['Description: ' + tool_desc],
                    title='Tool: ' + tool_name
                ),
                dbc.AccordionItem(
                    item_id='tool-output',
                    children=[
                        dbc.Accordion(
                            id='tool-output-inner-accordion',
                            children=[
                                dbc.AccordionItem(
                                    'Description: ' + out_desc,
                                    item_id=tool_id + '.' + out_type,
                                    title=out_type,
                                    style={
                                        'border-style': 'dashed'
                                    }
                                )
                                for out_desc, out_type in zip(out_desc_list, out_type_list)
                            ]
                        )
                    ],
                    title='Key Output(s)'
                )
            ],
            start_collapsed=True,
            flush=True
        )
    )

    return accordion_div


def generate_external_node_accordion(node, filename):
    """
    Create an accordion for the selected external node
    """
    accordion_div = html.Div(
        children=[
            dbc.Accordion(
                id='node-desc-accordion',
                children=[
                    dbc.AccordionItem(
                        item_id=node['id'],
                        children=[retrieve_external_node_desc(node, filename)],
                        title='External Input Data: ' + node['id'].split('.')[2]
                    )
                ],
                start_collapsed=True,
                flush=True
            ),
            dbc.AccordionItem(
                id='tool-output-inner-accordion',
                style={'display': 'none'}
            )
        ]
    )

    return accordion_div


def retrieve_external_node_desc(node, filename):
    """
    Retrieve information of the external node from the *pipeline.txt file
    """
    edge_list = pne.generate_edges(filename)
    ext_node_type = node['id'].split('.')[2]
    pipeline_df = pne.load_pipeline_file(filename)

    for idx, row in pipeline_df.iterrows():
        if row['source'] == node['id']:
            return row['ext_data_desc']

    # for edge in edge_list:
    #     if edge['data']['source'] == node['id']:
    #         target = edge['data']['target']
    #         tool = tools_root.find("./tool[@name='{}']".format(target.split('.')[1]))
    #         ext_input = tool.find("./ext-input/[input-type='{}']".format(ext_node_type))
    #
    #         ext_node_desc = ext_input.find('input-desc').text
    #
    #         return ext_node_desc

# generate_node_desc_accordion({'id': '3.qiime2_vsearch_merge-pairs', 'label': 'qiime2_vsearch_merge-pairs', 'timeStamp': 1721821099141})
