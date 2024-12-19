# Resume Tracker and PDF Generator

This tool was created for personal use and is not yet fully configurable.
It processes a Git repository, a Git tag, and a note, generating a unique ID
and adding it, along with the supplied information, to a JSON file. The tool
also creates a PDF file containing the unique ID.

## Setup and Requirements

### Prerequisites
Ensure the following tools are installed and configured on your system:
1. **Google Chrome**  
   - Assumed to be installed at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (MacOS default path).  
   - Update the path in the script if Chrome is installed elsewhere.  
2. **Pandoc**  
   - Download from [Pandoc's official site](https://pandoc.org/demos.html).  
   - Ensure Pandoc is available in your system's `PATH`.  

### Installation
No additional installation is required for this tool beyond the prerequisites.

## Example Usage
See https://github.com/sepn/resume-example for an example resume

To generate a PDF with this tool, run the following command:

```bash
python3 create_resume_pdf.py --repo ../resume --ref v1 --note "sent to colleague at Unicorn Co."