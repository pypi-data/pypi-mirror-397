"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from daccuracy.constant.project import NAME_MEANING, PROJECT_NAME, SHORT_DESCRIPTION


HEADER = f"""
<h2><b>{PROJECT_NAME}</b>: {NAME_MEANING}</h2>

<hr/>

<h3>About {PROJECT_NAME}: <small>See Below</small></h3>
"""

FOOTER = f"""
<h3>About {PROJECT_NAME}</h3>

<h4>Purpose</h4>

<p>
    {SHORT_DESCRIPTION}
</p>

<h4>Privacy</h4>

<p>
    Processed images are copied to the temporary folder {{}}.
</p>

<h4>Links</h4>

<ul>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/daccuracy/-/blob/master/README.rst" class="bgm">Documentation</a>
    </li>
    <li>
        <a href="https://src.koda.cnrs.fr/eric.debreuve/daccuracy/" class="bgm">Source code (Gitlab repository)</a>
    </li>
    <li>
        <a href="https://pypi.org/project/daccuracy/" class="bgm">Python Package Index (PyPI) page</a>
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
