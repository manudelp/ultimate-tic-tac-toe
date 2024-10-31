import os

def generate_tree_structure(root_dir, output_file):
    # Remove the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    with open(output_file, 'w') as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip node_modules, .git, .venv, and __pycache__ directories
            if any(ignored in dirpath.split(os.sep) for ignored in ['node_modules', '.git', '.venv', '__pycache__']):
                continue
            level = dirpath.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f'{indent}{os.path.basename(dirpath)}/\n')
            sub_indent = ' ' * 4 * (level + 1)
            for filename in filenames:
                if '__pycache__' in filename:
                    continue
                f.write(f'{sub_indent}{filename}\n')

if __name__ == "__main__":
    root_directory = '.'  # Change this to the directory you want to scan
    output_filename = 'structure.txt'
    generate_tree_structure(root_directory, output_filename)
    print(f'Tree structure saved to {output_filename}')