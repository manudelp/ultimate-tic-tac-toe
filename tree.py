import os

def generate_tree_structure(root_dir, output_file):
    # Define patterns to ignore based on gitignore
    ignore_patterns = [
        'node_modules', '.pnp', '.yarn', 'coverage', '.next', 'out', 'build',
        '.DS_Store', '*.pem', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
        '.env*', '.vercel', '*.tsbuildinfo', 'next-env.d.ts', '.cache', 
        '.pytest_cache', '__pycache__', '*.pyc', '.git', '.venv', '.gitignore'
    ]
    
    # Remove the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    
    with open(output_file, 'w') as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip node_modules, .git, .venv, venv, and __pycache__ directories
            # Skip directories and files in the gitignore list
            ignored_patterns = ['node_modules', '.pnp', '.yarn', 'coverage', '.next', 'out', 'build', 
                               '.DS_Store', '.env', '.vercel', '__pycache__', '.cache', '.pytest_cache',
                               '.git', '.venv', 'venv', 'tsbuildinfo', 'next-env.d.ts']
            if any(ignored in dirpath for ignored in ignored_patterns) or any(file.endswith(('.pem', '.pyc', '.tsbuildinfo')) for file in filenames):
                continue
                
            level = dirpath.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f'{indent}{os.path.basename(dirpath)}/\n')
            
            sub_indent = ' ' * 4 * (level + 1)
            for filename in filenames:
                # Skip files that match ignore patterns
                if any(
                    pattern == filename or
                    (pattern.startswith('*') and filename.endswith(pattern[1:]))
                    for pattern in ignore_patterns
                ):
                    continue
                f.write(f'{sub_indent}{filename}\n')

if __name__ == "__main__":
    root_directory = '.'  # Change this to the directory you want to scan
    output_filename = 'structure.txt'
    generate_tree_structure(root_directory, output_filename)
    print(f'Tree structure saved to {output_filename}')