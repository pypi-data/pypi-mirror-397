from glob import glob
from hashlib import md5
from json import dump
from pathlib import Path

from docutils.nodes import make_id
from docutils.nodes import section
from sphinx.errors import ExtensionError

def embed(app, doctree, docname):
    if docname not in app.embeddings:
        app.embeddings[docname] = []
    # title = app.env.titles.get(docname).astext()  # TODO: Don't assume it exists...?
    # app.embeddings[docname]["document"]["title"] = title
    config = app.config.sphinx_embeddings
    for node in doctree.traverse(section):
        xml = node.asdom().toxml()
        hash = md5(xml.encode("utf-8")).hexdigest()
        section_title = node[0].astext()  # TODO: I believe we can assume this one exists...?
        ids = node['ids']
        id = make_id(section_title)
        if id not in ids:
            raise ExtensionError(f"[sphinx-embeddings] Could not resolve section ID. Expected: {id} Found: {ids}")
        for provider in config:
            try: 
                match provider:
                    case "gemini":
                        # TODO: Move up to top? Use try/catch block with ImportError
                        from google import genai
                        gemini = genai.Client()
                        for model in config["gemini"]:
                            response = gemini.models.embed_content(model=model, contents=xml)
                            embedding = response.embeddings[0].values
                            app.embeddings[docname].append({
                                "provider": provider,
                                "model": model,
                                "type": "section",
                                "id": id,
                                "hash": hash,
                                "title": section_title,
                                "embedding": embedding[0:10]  # TODO
                            })
            except ModuleNotFoundError:
                print("[ERR] Extra dependency not found")
                print("[ERR] Fix: pip install sphinx-embeddings[{}]".format(provider))


def write(app, exception):
    if app.builder.format != "html" or exception:
        return
    # https://github.com/sphinx-doc/sphinx/blob/master/sphinx/builders/html/__init__.py#L1492
    suffix = "html" if app.config.html_file_suffix is None else app.config.html_file_suffix
    if app.config.html_baseurl == '':
        url = 'https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_baseurl'
        raise ExtensionError(f'[sphinx-embeddings] html_baseurl is required: {url}')
    embeddings = {}
    index = []
    outdir = str(app.outdir)
    for docname in app.embeddings:
        absolute_path = str(Path(outdir) / Path(f"{docname}.{suffix}"))
        embeddings[absolute_path] = app.embeddings[docname]
    for html_path in Path(outdir).glob(f"**/*.{suffix}"):
        if str(html_path) not in embeddings:
            continue
        embeddings_path = f"{str(html_path)}.embeddings.json"
        data = embeddings[str(html_path)]
        relative_path = embeddings_path.replace(f"{outdir}/", "")
        # TODO: Error if html_baseurl does not exist
        url = f"{app.config.html_baseurl}/{relative_path}"
        index.append(url)
        with open(embeddings_path, "w") as f:
            dump(data, f)
    well_known = Path(outdir) / Path(".well-known")
    if not well_known.exists():
        well_known.mkdir(parents=False, exist_ok=False)
    index_path = well_known / Path("embeddings.json")
    with open(index_path, "w") as f:
        dump(index, f)


def setup(app):
    app.embeddings = {}
    # TODO: Not sure about this schema
    config = {
        "models": {
            "gemini/gemini-embedding-001": {}  # opposed to "vertex/gemini-embedding-001"
        }
    }
    app.add_config_value('sphinx_embeddings', config, 'env')
    app.connect('doctree-resolved', embed)
    app.connect('build-finished', write)
    return {
        'version': '0.0.10',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
