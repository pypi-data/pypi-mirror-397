"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from pca_b_stream.constant.project import NAME_MEANING, PROJECT_NAME, SHORT_DESCRIPTION

DETAILS_LEGEND = {
    "m": "Max. value in array (= number of sub-streams)",
    "c": "Compressed",
    "e": "Byte order (a.k.a. endianness)",
    "t": "dtype code",
    "T": "dtype name",
    "o": "Enumeration order",
    "v": "First value per sub-stream (0: 0 or False, 1: non-zero or True)",
    "d": "Array dim.",
    "l": "Lengths per dim.",
}

HEADER = f"""
<h2><b>{PROJECT_NAME}</b>: {NAME_MEANING}</h2>

<hr/>

<h3>About {PROJECT_NAME}: <small>See Below</small></h3>
"""

FOOTER = f"""
<h3>Byte Stream Example</h3>

<p style="color:DarkGoldenRod">
    F?iamadKul!FYnvXe0x}}}}2|Q8~!vmgRl!P!OhbaA&lt;aWn=-V_-A}}}}Mq^+=X#oDN(G&<br/>
    (Copy and paste into Byte Stream input area, then convert to piecewise-constant array)
</p>

<h3>About {PROJECT_NAME}</h3>

<h4>Purpose</h4>

<p>
    {SHORT_DESCRIPTION}
</p>

<h4>Privacy</h4>

<p>
    Processed PCAs are copied to the temporary folder {{}}.
</p>

<h4>Links</h4>

<ul>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/pca-b-stream/-/blob/master/README.rst" class="bgm">Documentation</a>
    </li>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/pca-b-stream/" class="bgm">Source code (Gitlab repository)</a>
    </li>
    <li>
        <a href="https://pypi.org/project/pca-b-stream/" class="bgm">Python Package Index (PyPI) page</a>
    </li>
</ul>
"""

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

ul {
    list-style-type: disc;
    padding-left: 20px;
}

th, td {
    vertical-align: middle;
}

/* bgm=Blue, Green, Maroon. */
a.bgm:link {
    color: blue;
    text-decoration: none;
}
a.bgm:visited {
    color: green;
    text-decoration: none;
}
a.bgm:hover {
    color: maroon;
    text-decoration: underline;
}
a.bgm:active {
    color: maroon;
    text-decoration: underline;
}

.main_container {
  max-width: 72em;
  margin: auto;
}
"""
