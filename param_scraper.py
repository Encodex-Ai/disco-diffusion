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
                if '@param' in line and not line.startswith('#'):
                    print(line)
                    parts = line.split('#')[0].strip().split('=')
                    print(parts)
                    if len(parts) >= 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip().split()[0]  # Extract the parameter value
                        params[param_name] = param_value

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(params, file, indent=4)

# Example usage
scan_ipynb_for_params('./Disco_Diffusion.ipynb', 'params.json')

