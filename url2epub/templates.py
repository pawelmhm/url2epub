html1 = """
<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>

<p>My first paragraph.</p>

</body>
</html>
"""

html2 = """
<!DOCTYPE html>
<html>
<body>

<h1>Some different heading</h1>

<p>My first paragraph.</p>

</body>
</html>
"""


container = """
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
	<rootfiles>
		<rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>
"""

package_opf = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:dcterms="http://purl.org/dc/terms/" version="3.0" xml:lang="en"
	unique-identifier="pub-identifier">
	<metadata>
		<dc:identifier id="pub-identifier">urn:isbn:9781449328030</dc:identifier>
		<dc:title id="pub-title">{title}</dc:title>
		<dc:language id="pub-language">en</dc:language>
		<dc:date>{date}</dc:date>
		<meta property="dcterms:modified">{date}</meta>
		<dc:creator id="pub-creator12">{creator}</dc:creator>
	</metadata>
	<manifest>
		<item id="htmltoc" properties="nav" media-type="application/xhtml+xml" href="navs.xhtml"/>
	</manifest>
    <spine>
		<itemref idref="htmltoc" linear="yes"/>
    </spine>
</package>
"""

mimetype = "application/epub+zip"

nav = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en"
	lang="en">
	<head>
		<title>Hacker News Content</title>
	</head>
	<body>
		<h1>Hacker News</h1>
		<nav epub:type="toc" id="toc">
			<h2>Table of Contents</h2>
			<ol id='content_list'>
			</ol>
		</nav>
	</body>
</html>"""


