import json
from pathlib import Path
from typing import List

from pymultirole_plugins.v1.schema import Document, DocumentList

from pysegmenters_md_splitter.md_splitter import MarkdownSplitterSegmenter, MarkdownSplitterParameters, \
    ExperimentalMarkdownSyntaxTextSplitter


def test_md_splitter():
    testdir = Path(__file__).parent
    source = Path(testdir, "data/deontobot_v0-document-wikijsid_4.json")
    with source.open("r") as fin:
        jdocs = json.load(fin)
    original_docs = [Document(**jdoc) for jdoc in jdocs]
    model = MarkdownSplitterSegmenter.get_model()
    model_class = model.construct().__class__
    assert model_class == MarkdownSplitterParameters
    segmenter = MarkdownSplitterSegmenter()
    parameters = MarkdownSplitterParameters()
    docs: List[Document] = segmenter.segment(original_docs, parameters)
    assert len(docs) == 1
    doc0 = docs[0]
    assert len(doc0.sentences) == 115
    for sent in doc0.sentences:
        ctext = doc0.text[sent.start:sent.end]
        print("===========================================================")
        print(ctext)

    dl = DocumentList(__root__=docs)
    result = Path(testdir, "data/deontobot_v0-document-wikijsid_4_segmented.json")
    with result.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def test_splitter():
    text = """[^0] [^0]: *Average from January to December 2024

```
Non-binding

```
** Topics = last version articles
** Actualisations = all versions articles
```
# AFP STORIES IN ARABIC

## Coverage
"""
    splitter = ExperimentalMarkdownSyntaxTextSplitter(headers_to_split_on=-1,
                                                      strip_headers=False)
    chunks = splitter.split_text(text)
    ctext = ""
    for chunk in chunks:
        ctext += chunk.text
        cmetas = {k: v for k, v in chunk.metadata.items() if isinstance(k, int)}
        headers = [v for k, v in sorted(cmetas.items())]
        smetadata = {}
        if headers:
            smetadata['Headers'] = ' / '.join(headers)
    assert ctext == text
