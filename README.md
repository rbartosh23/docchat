# docchat

A command-line chatbot that answers questions about the files in a folder. It sends your messages to a language model through the Groq API. The model can look at your files using four tools: `ls`, `cat`, `grep`, and `calculate`.

## Install

    python -m pip install .

## Use

Put your key in a `.env` file (`GROQ_API_KEY=your_key`), then run:

    chat

Press Ctrl+C or Ctrl+D (Ctrl+Z then Enter in PowerShell) to exit.

You can also run a tool yourself by typing a command that starts with `/`:

    /ls .
    /cat README.md
    /grep TODO *.py
    /calculate 2 + 3

## Example: markdown-compiler

````
$ cd test_projects/markdown-compiler
$ chat
chat> /ls .
README.md  example  markdown_compiler  pyproject.toml  requirements.txt
chat> Which function handles bold text?
The compiler uses two functions for bold text, depending on the Markdown delimiter:

- **Double‑asterisk (`**bold**`)** → `compile_bold_stars(line)`
- **Double‑underscore (`__bold__`)** → `compile_bold_underscore(line)`

Both are defined in `markdown_compiler/util/line_functions.py`.
````

The chatbot looked through my project’s files and named the exact function that handles bold text, which showed me how my compiler is organized.

## Example: ebay-scraper

````
$ cd test_projects/ebay-scraper
$ chat
chat> /ls .
README.md  drill press.json  ebay-dl.py  garden tools.json  stuffed animal.json
chat> What does this project do?
The project is a simple **eBay scraper** written in Python.  
Its purpose is to collect structured information about items that appear in eBay search results and save that data to a JSON file that other programs can read.

### How it works

1. **User supplies a search term** (e.g., `"drill press"`).  
2. The script fetches the first 10 pages of results for that term.  
   * It can download them live from eBay using `requests`, or it can read pre‑saved “practice” HTML pages from a folder (useful when eBay blocks the scraper).  
3. Using **Beautiful Soup** it parses each page and extracts the following details for every listing:
   * `name` – item title  
   * `price` – price in cents (e.g. $11.95 → 1195)  
   * `status` – condition (“Brand New”, “Pre‑owned”, etc.)  
   * `shipping` – shipping cost in cents (free → 0)  
   * `free_returns` – `True` if free returns are offered, otherwise `False`  
   * `items_sold` – how many units have been sold  
4. Any missing data is stored as `null` (Python’s `None`).  
5. All listings are written to a JSON file named after the search term (e.g., `drill press.json`).

### Running the script

```bash
python ebay-dl.py --search "SEARCH TERM"
```

If you want to use the practice pages (which the repository ships with), add `--pages-dir practice-pages`:

```bash
python ebay-dl.py --search "garden tools" --pages-dir practice-pages
```

The repository already contains three example JSON files (`garden tools.json`, `drill press.json`, `stuffed animal.json`) that were produced using the practice pages.

In short, the project automates the collection of eBay product data and outputs it in a convenient, machine‑readable JSON format.
chat> Which file handles headings?
In this repository the only file that contains “headings” (the markdown title lines that start with `#`) is **`README.md`**.  
The Python script (`ebay-dl.py`) does not generate or manipulate any headings; it simply parses eBay HTML and writes the extracted data to JSON.
````

The chatbot summarized the scraper accurately from its files, and it correctly pointed out that this project has no code that handles headings.

## Example: lab-homepage

````
$ cd test_projects/lab-homepage
$ chat
chat> /ls .
Little-Me.jpg  README.md  index.html  style.css
chat> Which file handles headings?
The headings are defined in **`index.html`**.  
In that file you’ll see the `<h1 id="top">My First Web Page!</h1>` tag (and any other heading tags you may add).
````

The chatbot found the right file and quoted the exact heading tag from it.