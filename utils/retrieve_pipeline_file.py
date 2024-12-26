import os
import xml.etree.ElementTree as ET

utils_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_list_filepath = os.path.join(utils_dir, '..', 'pipeline', 'pipeline_list.xml')

pipeline_tree = ET.parse(pipeline_list_filepath)
pipeline_root = pipeline_tree.getroot()


def get_pipeline_list():
    return [
        {
            'name': workflow.get('name'),
            'file': workflow.find('file').text
        }
        for workflow in pipeline_root.findall('workflow')
    ]
