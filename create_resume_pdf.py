import argparse
import os
import subprocess
import json
import sys
import uuid
import shutil


def run_command(command, cwd=None, check=True):
    """Runs a shell command and returns its output."""
    try:
        result = subprocess.run(command, cwd=cwd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.stderr)
        sys.exit(1)

def ensure_clean_working_tree(repo_path):
    """Ensures the working tree is clean."""
    status = run_command(['git', 'status', '--porcelain'], cwd=repo_path)
    if status:
        print("Working tree is not clean. Please commit or stash your changes.")
        sys.exit(1)

def checkout_ref(repo_path, git_ref):
    """Checks out the specified git ref."""
    run_command(['git', 'checkout', git_ref], cwd=repo_path)

def add_entry_to_json(json_path, git_hash, note):
    """Adds a new entry to the JSON file."""
    if not os.path.exists(json_path):
        data = {}
    else:
        with open(json_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print("Invalid JSON file. Exiting.")
                sys.exit(1)
    
    new_id = str(uuid.uuid4())
    data[new_id] = {
        "git hash": git_hash,
        "note": note
    }
    
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Added entry with ID {new_id} to {json_path}")
    return new_id

def create_temp_dir(output_dir):
    # Create temp directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

def run_pandoc(repo_path, output_dir):
    """Runs the pandoc command to convert resume.md to resume.html."""
    md_file = os.path.join(repo_path, 'resume.md')
    output_file = os.path.join(output_dir, 'resume.html')
    css_file = 'style.css'

    if not os.path.exists(md_file):
        print(f"Error: resume.md not found in {repo_path}")
        sys.exit(1)

    command = ['pandoc', '-s', md_file, '-o', output_file, '-c', css_file]
    print("Running pandoc to generate resume.html...")
    run_command(command)
    print(f"Generated {output_file}")

def copy_and_modify_css(repo_path, output_dir, generated_id):
    """Copies style.css from the repo to the temp directory and replaces {{ref-id}} with the generated ID."""
    css_repo_file = os.path.join(repo_path, 'style.css')
    css_temp_file = os.path.join(output_dir, 'style.css')

    if not os.path.exists(css_repo_file):
        print(f"Error: style.css not found in {repo_path}")
        sys.exit(1)
    
    # Copy style.css to temp directory
    shutil.copy(css_repo_file, css_temp_file)
    print(f"Copied style.css to {output_dir}")

    # Replace {{ref-id}} in the copied style.css
    with open(css_temp_file, 'r') as file:
        css_content = file.read()
    ref_id = generated_id.split('-')[-1]
    css_content = css_content.replace("{{ref-id}}", ref_id)
    with open(css_temp_file, 'w') as file:
        file.write(css_content)
    print(f"Updated style.css with ref-id: {ref_id}")

def generate_pdf_with_chrome(output_dir):
    """Runs Google Chrome in headless mode to convert the HTML file to PDF."""
    # Paths for input HTML and output PDF
    html_file = os.path.join(output_dir, 'resume.html')
    pdf_file = os.path.join(output_dir, 'output.pdf')
    
    # Check if HTML file exists
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
        sys.exit(1)
    
    # Chrome headless command
    chrome_command = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_file}",
        "--no-pdf-header-footer",
        f"file://{html_file}"
    ]
    
    print("Generating PDF with Google Chrome headless mode...")
    run_command(chrome_command)
    print(f"Generated PDF: {pdf_file}")

def main():
    parser = argparse.ArgumentParser(description="A tool to manage resume versions, track changes in a Git repository, generate HTML and PDF outputs, and update a JSON log with metadata.")
    parser.add_argument('--repo', required=True, help="Path to the git repository")
    parser.add_argument('--ref', required=True, help="Git hash or tag to checkout")
    parser.add_argument('--note', required=True, help="A freeform note string")
    parser.add_argument('--json', default="data.json", help="Path to the JSON file (default: data.json)")
    
    args = parser.parse_args()
    
    repo_path = os.path.abspath(args.repo)
    if not os.path.isdir(repo_path):
        print(f"Invalid repository path: {repo_path}")
        sys.exit(1)

    ensure_clean_working_tree(repo_path)
    checkout_ref(repo_path, args.ref)
    git_hash = run_command(['git', 'rev-parse', 'HEAD'], cwd=repo_path)
    ref_id = add_entry_to_json(args.json, git_hash, args.note)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    create_temp_dir(output_dir)
    run_pandoc(repo_path, output_dir)
    copy_and_modify_css(repo_path, output_dir, ref_id)

    generate_pdf_with_chrome(output_dir)

if __name__ == "__main__":
    main()