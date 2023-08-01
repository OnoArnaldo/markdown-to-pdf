# markdown-to-pdf

## Install

Create `venv`:
```shell
python3.11 -m venv venv
source venv/bin/activate
```

Install package:
```shell
pip install --upgrade pip
pip install -r requirements.txt
pip install .
```

or from gitHub:
```shell
pip install git+https://github.com/OnoArnaldo/markdown-to-pdf
```

in case the project is still private:
```shell
pip install git+ssh://git@github.com/OnoArnaldo/markdown-to-pdf
```


## Introduction

`md2pdf` process the markdown following the steps bellow.

```mermaid
---
title: md2pdf
---
flowchart
    markdown([markdown]) --> |generates html and dict<br>no &#123&#123 value &#125&#125 replacement| html_headers([html + headers])
    html_headers --> |generates html replacing &#123&#123 value &#125&#125 | html([html])
    html --> |convert html to dict|dict([dict])
    dict --> |process dict to generate pdf|pdf([pdf])
```

> The configuration file should be set with
> the last html in mind.


## Usage

Generating the pdf file.

```python
from pathlib import Path

from md2pdf import loads_config, load_config, Md2Pdf

ROOT = Path(__file__).parent
CONFIG_FILE = ROOT / 'config.toml'
MD_FILE = ROOT / 'document.md'
PDF_FILE = ROOT / 'document.pdf'

# CONFIG FROM TEXT
config = loads_config(CONFIG_FILE.read_text())

# CONFIG FROM FILE
with CONFIG_FILE.open() as f:
    config = load_config(f)

# FROM FILE
(Md2Pdf()
 .setup(config)
 .build_from_file(MD_FILE)
 .save(PDF_FILE,
       title='Document 1',
       name='My Name',
       keywords=['Document', 'sample'],
       version='abc'))

# FROM MD TEXT
text = MD_FILE.read_text()

(Md2Pdf()
 .setup(config)
 .build_from_md(text)
 .save(PDF_FILE,
       title='Document 1',
       name='My Name',
       keywords=['Document', 'sample'],
       version='abc'))

# FROM HTML TEXT
# using jinja2 syntax, without access to other files.
text = (ROOT / 'document.html').read_text()

(Md2Pdf()
 .setup(config)
 .build_from_html(text,  
                  name="My Name", 
                  company="My Company")
 .save(PDF_FILE,
       title='Document 1',
       name='My Name',
       keywords=['Document', 'sample'],
       version='abc'))
```


### Configuration

The configuration file is divided in 4 sections:

* Fonts: To add specific fonts to the document 
    (example: some font you downloaded from Google fonts).
* Styles: Configure the styles than can be used in the document.
* Reports: Definition of the style to be used based on the 
    combination of attributes.
* Defaults: Default values to be used by the styles and reports.

> Check the file `tests/config.toml`.


#### Fonts:

Definition:
```toml
[[fonts]]
name = "Font Name"
regular = "path-to/Font-Regular.ttf"
bold = "path-to/Font-Bold.ttf"
italic = "path-to/Font-Italic.ttf"
bold_italic = "path-to/Font-BoldItalic.ttf"
```

Multiple fonts can be defined in the configuration. In case you don't have 
one of the styles, of the value from the style you have.

The path can be absolute or relative (the root will be set in the execution).


#### Styles:

Definition:
```toml
[[styles]]
name = "Style Name"
font_name = "Font Name"
font_size = 12
space_before = 5
space_after = 10
alignment = "TA_LEFT"
```

> Check appendix for all the options.

> The values in this section will overwrite the values in `defaults` section.

Multiple styles can be defined in the configuration. Note that, 
despite the naming style in reportlab uses mixedCase, the configuration will use 
lower_case_with_underscores format to be consistent with python
naming conventions.


#### Reports

Definition:
```toml
[[reports]]
style = "Style Name"

[[reports.attributes]]
name = "attr-name"
value = "attr-value"
```

Multiples reports ca be defined in the configuration, and multiple attributes
can be defined in each report.

* `Name` can be the attribute name or the value `tag`.
* `Value` can be the attribute value or the tag name.

examples:
```toml
[[reports.attributes]]
name = "tag"
value = "h2"

[[reports.attributes]]
name = "id"
value = "subtitle"
```

> The order of the reports in the configuration file matters!
> It will use the style of the first configuration it finds.


#### Defaults

Definition
```toml
[defaults.report]
style = "Style Name"

[defaults.style]
font_size = 10
alignment = "TA_JUSTIFY"
allow_widows = 0
space_before = 10
space_after = 10
```

> Check appendix for all style options.


### Template

Simple example:

```markdown
name= "The Name"
company= "The Company"

# Hello {{ name }}

## Hello company {{ company }}

Below is a list:

* item 1
* item 2
```

#### Using headers

The headers are key-value items in the beginning of the document, you have to add a blank line before the content.

```markdown
name: My Name
company: My Company

# {{ company }}

## {{ name }}
```


#### Adding attributes

Adding in headers:

```markdown
# In headers {: #the-id .the-class .another-class custom="value" }
```

Adding to paragraphs:

```markdown
This is a paragraph.
{: #the-id .the-class .another-class custom="value" }
```

Adding to list:

```markdown
* item-1
* item-2
* item-3
{: #the-id .the-class .another-class custom="value" }
```

> Note that the attributes will be assigned to the `item-3` only


For all the examples above, this will be the result:

```json
{
  "id": "the-id",
  "class": "the-class another-class",
  "custom": "value"
}
```

##### Special attributes

Keep together: it will keep all the elements together, in the same page, plus the next element without the attribute.

```markdown
# The title {: .keep-together }

The paragraph 1.
{: .keep-together}

The paragraph 2.
```

> In this example, the title and both paragraphs will stay together in the same page.

Key value: it will treat the line as a key/value line, separated by `:`.

```markdown
paragraph key: paragraph value
{: .key-value style="italic,bold,underscore"}

* item key 1: item value 1
* item key 2: item value 2
* item key 3: item value 3
{: .key-value}
```

> The default style is `bold`.

> If you want to use `:` as part of the key or value, you will have to escape it with `&#58;`.


#### Functions and constants

##### Special functions

```markdown
Change style in the middle of the paragraph.
Some examples: {{ underscore("aaaa") }}, {{ italic("bbbb") }}, {{ bold("cccc") }}, dddd
They can be combined: {{ underscore(italic(bold("eeee"))) }}, ffff
```


##### Add functions and constants

> This is a workaround.

```python
from datetime import datetime
from md2pdf import parser

def today():
    return datetime.utcnow().strftime('%d-%m-%Y')

_original = parser.build_env

def new_build_env(*args, **kwargs):
    env = _original(*args, **kwargs)
    env.globals['today'] = today
    env.globals['company'] = 'My Company'

    return env

parser.build_env = new_build_env
```

In the markdown:

```markdown
# {{ company }}

Today is {{ today() }}.
```


## Appendix

#### Paragraph Style

This is based on `reportlab.lib.styles.ParagraphStyle`.

> Note that the `mixedCase` was replaced by `lower_case_with_underscores`.

```toml
font_name = "Helvetica"
font_size = 10
leading = 12
left_indent = 0
right_indent = 0
first_line_indent = 0
alignment = "TA_LEFT"
space_before = 0
space_after = 0
bullet_font_name = "Helvetica"
bullet_font_size = 10
bullet_indent = 0
text_color =  "black"
#back_color = None
#word_wrap = None
border_width =  0
border_padding =  0
#border_color =  None
#border_radius =  None
allow_widows =  1
allow_orphans =  0
#text_transform = None
#end_dots = None
split_long_words = 1
underline_width =  ""
bullet_anchor =  "start"
justify_last_line =  0
justify_breaks =  0
space_shrinkage =  0.05
strike_width = ""              #stroke width
underline_offset = "-0.125*F"  #fraction of fontsize to offset underlines
underline_gap = 1              #gap for double/triple underline
strike_offset = "0.25*F"       #fraction of fontsize to offset strikethrough
strike_gap = 1                 #gap for double/triple strike
link_underline = 0
hyphenation_lang = ""
uri_waste_reduce = 0
embedded_hyphenation = 0
```
