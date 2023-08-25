import os
# Importing required libraries
import os
from config import workflows, IMAGE_PATH

def get_workflow(workflow_name):
    for workflow in workflows['workflows']:
        if workflow['name'] == workflow_name:
            return workflow
    return None

def get_category(workflow, category_name):
    for category in workflow['categories']:
        if category['name'] == category_name:
            return category
    return None

def get_style(category, style_name):
    for style in category['styles']:
        if style['name'] == style_name:
            return style
    return None

def get_prompt(workflow_name, category_name, style_name):
    workflow = get_workflow(workflow_name)
    if workflow is None:
        return None

    category = get_category(workflow, category_name)
    if category is None:
        return None

    style = get_style(category, style_name)
    if style is None:
        return None

    return style['prompt']

def save_image(image, filename):
    file_path = os.path.join(IMAGE_PATH, filename)
    with open(file_path, 'wb') as img_file:
        img_file.write(image)
    return file_path
