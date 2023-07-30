from pathlib import Path
from md2pdf import Md2Pdf, loads_config

ROOT = Path(__file__).parent
CONFIG_FILE = ROOT / 'config.toml'
DOC_DIR = ROOT / 'docs'
OUT_DIR = ROOT / 'output'

# Create configuration object
config = loads_config(CONFIG_FILE.read_text())

# Create document version (this is optional)
version = Md2Pdf.version(config)

# Execute the pdf creator
Md2Pdf()\
    .setup(config, root_dir=ROOT)\
    .build_from_file(DOC_DIR / 'sample.md')\
    .save(OUT_DIR / 'sample.pdf',
          name='Your Name',
          title='Sample',
          version=version,
          keywords=['pdf generator', 'from markdown'])
