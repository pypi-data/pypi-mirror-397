"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from pca_b_stream.constant import NAME_MEANING, PROJECT_NAME, SHORT_DESCRIPTION


PCA_SIZE_TEMPLATE = "{:_} bytes"
BYTE_STREAM_LENGTH_TEMPLATE = "{:_} characters"

HEADER = f"""
<h2><b>{PROJECT_NAME}</b>: {NAME_MEANING}</h2>

<hr/>

<h3>About {PROJECT_NAME}: <small>See Below</small></h3>

<hr/>
"""

FOOTER = (
    """
<h3>Byte Stream Example</h3>

<p style="color:DarkGoldenRod">
    F?iamadKul!FYnvXe0x}}2|Q8~!vmgRl!P!OhbaA&lt;aWn=-V_-A}}Mq^+=X#oDN(G&<br/>
    (Copy and paste into Byte Stream input area, then convert to piecewise-constant array)
</p>
"""
    + "<h3>About "
    + PROJECT_NAME
    + """</h3>

<h4>Purpose</h4>

<p>"""
    + SHORT_DESCRIPTION
    + """</p>

<h4>Privacy</h4>

<p>
    Processed PCAs are copied to the temporary folder {}.
</p>

<h4>Links</h4>

<ul>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/pca-b-stream/-/blob/master/README.rst">Documentation</a>
    </li>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/pca-b-stream/">Source code (Gitlab repository)</a>
    </li>
    <li>
        <a href="https://pypi.org/project/pca-b-stream/">Python Package Index (PyPI) page</a>
    </li>
</ul>
"""
)

STYLE = """
body {
    background-color: LightGray;
    font-family: sans-serif, monospace;
    font-size: 12pt;
}

h2 {
    font-size: 24pt;
    color: Brown;
}
h3 {
    font-size: 20pt;
    color: Chocolate;
    text-align: center;
}
h4 {
    font-size: 16pt;
    color: DarkMagenta;
}

th, td {
    vertical-align: middle;
}

.main_container {
  max-width: 72em;
  margin: auto;
}
"""
