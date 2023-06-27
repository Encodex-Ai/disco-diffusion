import json
import nbformat

def scan_ipynb_for_params(ipynb_path, json_path):
    with open(ipynb_path, 'r', encoding='utf-8') as file:
        notebook = nbformat.read(file, as_version=4)

    params = {}
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            lines = cell['source'].split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                if '@param' in line:
                    parts = line.split('@param')[1].split('#')[0].strip().split('=')
                    param_name = parts[0].strip()
                    param_value = parts[1].strip()
                    params[param_name] = param_value

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(params, file, indent=4)

# Example usage
scan_ipynb_for_params('path/to/your/notebook.ipynb', 'params.json')
