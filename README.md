# Indian metrical texts

This repository includes several texts on meter, with an initial focus on Sanskrit and Prakrit. The texts have been either typed up manually or OCRed. In the latter case, the texts need to be proofread and [TEI](https://tei-c.org/guidelines/p5/) markup needs to be added, manually or semi-manually.

## Texts
OCR > proofreading and TEI structure > validation

### TEI elements

``<div type="commentary-block"> ... </div>`` for chunks of text that include commentary and the base text together.

``<quote type="base-text"> ... </quote>`` for the base text (whether prose or verse or both).

``<note type="chāyā"> ... </note>`` for the Sanskrit translation (*chāyā*) of a Prakrit passage, usually a verse.

``<lg> ... </lg>`` for verse (line groups). This must include ``<l>`` elements (lines).

``<p>`` for prose paragraphs. This must include ``<s>`` elements (sentences).

For apparatus entries, use ``<app> ... </app>``, which typically includes two further elements:
- ``<lem wit="#A"> ... </lem>`` for the lemma (the reading selected by the editor) presented in witness **A**
- ``<rdg wit="#B"> ... </rdg>`` for a variant reading (not selected by the editor) represented in witness **B**
The value of ``@wit`` is usually a reference to a manuscript. Other attribute options for ``<lem>`` and ``<rdg>`` are ``@resp`` (responsibility, usually a person), ``@source`` (source, usually a printed text). ``<app>`` can include ``<note>`` elements as well.


Credits:

Andrew Ollett, Teo Ruskov, Tom Jennings, Purnima Pal