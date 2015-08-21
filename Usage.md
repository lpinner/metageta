# Usage #
To use MetaGeta as provided, the first step is to crawl the filesystem to locate imagery and extract metadata to a spreadsheet. Writing to a spreadsheet allows for quality control, such as removal of records, checking for duplicates, bulk updates, etc. It also allows the addition of extra metadata fields such as contacts, use and access constraints etc. Information on additional metadata fields can be found [here](http://metageta.googlecode.com/svn/trunk/doc/files/transforms-module.html).

If you don't like spreadsheets, it's quite simple to roll your own script that writes straight to XML, database, etc... Check out the [API documentation](http://metageta.googlecode.com/svn/trunk/doc/index.html) for more info.

You can run the crawler and transform applications by simply double clicking the runcrawler/runtransform.[bat|sh] files.  Don't try to run any **.py files directly unless you have set up your environment to suit.**

You can also run the crawler and transform applications without the directory/files entry GUI popping up by passing arguments to runcrawler/runtransform.[bat|sh].

<pre>Usage: runcrawler.bat/sh [arguments]<br>
<br>
Run the metadata crawler. If no arguments are passed, a dialog box pops up.<br>
<br>
Options:<br>
-h, --help       show this help message and exit<br>
-d dir           The directory to crawl<br>
-m media         CD/DVD ID<br>
-x xls           Output metadata spreadsheet<br>
-u, --update     Update existing crawl results<br>
-o, --overviews  Generate overview images<br>
--debug          Turn debug output on<br>
--nogui          Don't show the GUI progress dialog<br>
--keep-alive     Keep this dialog box open<br>
</pre>

The information extracted can then be transformed into XML. Currently only the ANZLIC Profile (ISO 19139) metadata schema is implemented for XML transformation, however more stylesheets can be [added easily](http://metageta.googlecode.com/svn/trunk/doc/files/transforms-module.html).

<pre>Usage: runtransform.bat/sh [arguments]<br>
<br>
Transform metadata to XML. If no arguments are passed, a dialog box pops up.<br>
<br>
Options:<br>
-h, --help  show this help message and exit<br>
-d dir       The directory to output metadata XML to<br>
-x xls       Excel spreadsheet to read metadata from<br>
-t xsl       XSL transform {*.xsl|"ANZLIC Profile"}<br>
-m           Create Metadata Exchange Format (MEF) file<br>
--nogui      Don't show the GUI progress dialog<br>
--keep-alive Keep this dialog box open<br>
--debug      Turn debug output on<br>
</pre>

Basic API documentation may be found [here](http://metageta.googlecode.com/svn/trunk/doc/index.html).