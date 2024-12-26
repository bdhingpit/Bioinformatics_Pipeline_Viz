import xml.etree.ElementTree as ET
import pandas as pd
import os

utils_dir = os.path.dirname(os.path.abspath(__file__))
tools_list_filepath = os.path.join(utils_dir, '..', 'pipeline', 'tools_list2.xml')

tree = ET.parse(tools_list_filepath)
root = tree.getroot()


def load_pipeline_file(pipeline_filename):
    try:
        return pd.read_csv('pipeline/{}'.format(pipeline_filename), sep='\t')
    except NameError:
        return None


def generate_edges(pipeline_filename):
    """
    Create dictionary of edges.
    """
    pipeline_df = load_pipeline_file(pipeline_filename)

    edges = []

    for idx, row in pipeline_df.iterrows():
        source_split = row['source'].split('.', maxsplit=1)
        tool_output_split = source_split[1].rsplit('.', maxsplit=1)  # Some tool names have '.'

        # If the source data is not an output of previous step in workflow (i.e. external node)
        if tool_output_split[0] == 'ext_data':
            edges.append({'data': {'source': row['source'], 'target': row['target']}})

        # If the source data is an output of a previous step in the workflow
        else:
            output_files_list = get_output_text(tool_output_split[0])

            for output_num in tool_output_split[1].split(','):
                file_output_src = (source_split[0], tool_output_split[0], output_files_list[int(output_num) - 1])
                edges.append({'data': {'source': '.'.join(file_output_src), 'target': row['target']}})

    return edges


def generate_nodes(pipeline_filename):
    """
    Create dictionary of nodes
    """
    pipeline_df = load_pipeline_file(pipeline_filename)

    nodes = []

    for idx, row in pipeline_df.iterrows():
        source_split = row['source'].split('.')
        target_split = row['target'].split('.', maxsplit=1)

        # For the initial file/s (i.e. external nodes)
        if source_split[1] == 'ext_data':
            nodes.append({'data': {'id': row['source'], 'label': source_split[2]}})

        # For the parent nodes
        nodes.append({'data': {'id': row['target'], 'label': target_split[1]}})

        # For the output/s of the parent nodes
        output_files_list = get_output_text(target_split[1])

        for output_file in output_files_list:
            nodes.append({'data': {'id': row['target']+'.'+output_file, 'parent': row['target']}})

    return nodes


def get_output_text(tool_name):
    for tool in root.iter('tool'):
        if tool.get('name') == tool_name:
            tool_output_list = tool.findall('output')

            return [output.find('output-type').text for output in tool_output_list]

    return None


def define_cytoscape_layout():
    layout = {
        'name': 'cola',
        'alignment': 'vertical',
        'ungrabifyWhileSimulating': True,
        'nodeSpacing': 20
    }

    return layout


def define_cytoscape_style():
    style = {
        'width': '100%',
        'height': '100%'
    }

    return style


def define_cytoscape_stylesheet():
    stylesheet = [
        {
            'selector': 'edge',
            'style':
                {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                }
        },
        {
            'selector': 'node',
            'style': {
                'content': 'data(label)',
                'font-size': 8,
                'color': '#3f4148'
            }
        }
    ]

    return stylesheet
