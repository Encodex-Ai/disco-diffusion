import json
import nbformat

def extract_param_value(value_str, param_type):
    if param_type.isspace():
        return value_str

    # Detect the type based on patterns in param_type
    param_type = param_type.lower()
    if 'number' in param_type or 'float' in param_type or 'int' in param_type:
        try:
            return int(value_str)
        except ValueError:
            try:
                return float(value_str)
            except ValueError:
                return value_str
    elif 'boolean' in param_type:
        return value_str.lower() == 'true'
    elif 'string' in param_type:
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
        else:
            return value_str
    else:
        return value_str



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
                    split_line = line.strip().split('#')
                    parts = split_line[0].split('=')
                    if len(parts) >= 2:
                        param_name = parts[0].strip()
                        param_value_str = parts[1].strip()  # Extract the parameter value
                        param_value = extract_param_value(param_value_str, split_line[1].strip("@param"))
                        params[param_name] = param_value
                         

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(params, file, indent=4)
        # print(params)

# Example usage
scan_ipynb_for_params('./Disco_Diffusion.ipynb', 'params.json')

