# -*- coding: utf-8 -*-
# Copyright (c) 2013 Australian Government, Department of the Environment
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

r'''
XSL transforms
==============
Utility functions to assist XSL transforms

Adding another stylesheet
-------------------------
    - Create a new/add an existing .xsl file that transforms crawler output (schema described below) to your XML schema.
    - Create an xml file that describes your XML schema (see below)
    - Save the xsl & xml file to the lib/transforms directory, it will be automatically available
Note: You may also pass the filepath to an external XSL stylesheet to the L{Transform} function.

Metadata schema
---------------
The following schema defines a simple XML format which holds extracted metadata
(see L{DictToXML} and L{ListToXML}) to be transformed by an XSL stylesheet to
various XML metadata schemas::
    <?xml version="1.0" encoding="UTF-8" ?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:element name="crawlresult">
        <xs:complexType>
          <xs:sequence>
            <xs:element ref="{FIELD}" />
          </xs:sequence>
        </xs:complexType>
      </xs:element>
      <xs:element name="{FIELD}">
        <xs:complexType mixed="true" />
      </xs:element>
    </xs:schema>
Where: {FIELD} are the fields defined in L{formats.fields}, plus any additional metadata elements you pass in.
For example, you can pass additional metadata elements in by adding them to the spreadsheet
which is passed to L{runtransform.py<runtransform>}.
Additional metadata elements for existing XSL stylesheets will be documented below.

Stylesheet description schema
-----------------------------
The following schema defines an XML file that describes an XSL stylesheet to be used by this module
to transform from the simple XML format defined above to various XML metadata schemas,
e.g. the ANZLIC Metadata Profile::
    <?xml version="1.0" encoding="UTF-8" ?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:element name="stylesheet">
        <xs:complexType>
          <xs:attribute name="name" type="xs:string" use="required" />
          <xs:attribute name="file" type="xs:string" use="required" />
          <xs:attribute name="description" type="xs:string" use="required" />
        </xs:complexType>
      </xs:element>
    </xs:schema>

Additional metadata elements
----------------------------
- anzlic_iso19139.xsl
  - Attributes below are not populated automatically, but may be manually added to the spreadsheet and will be included in the output XML/MEF metadata
  - NOTE - Some items require specific syntax, see the examples!
  - NOTE - item names are cAse SensitiVe

  Attributes::
    |Attribute                         |Note                         |Example
    |----------------------------------|-----------------------------|------------------------
    |AbsoluteExternalPositionalAccuracy|                             |Some text
    |----------------------------------|-----------------------------|------------------------
    |abstract                          |                             |This is the abstract for
    |                                  |                             |some dataset
    |----------------------------------|-----------------------------|------------------------
    |source                            |                             |Where we got the data from
    |----------------------------------|-----------------------------|------------------------
    |lineage                           |                             |What has been done to the data
    |----------------------------------|-----------------------------|------------------------
    |title                             |                             |ALOS pansharpened imagery
    |                                  |                             |for Coongie Lakes (2.5m)
    |----------------------------------|-----------------------------|------------------------
    |accessConstraints                 |                             |Data for INTERNAL use only!
    |----------------------------------|-----------------------------|------------------------
    |useConstraints                    |                             |The following acknowlegement
    |                                  |                             |must be incuded with any map
    |                                  |                             |that contains these data:
    |                                  |                             |blah blah blah
    |----------------------------------|-----------------------------|------------------------
    |ANZLICKeyword                     |More than one ANZLICKeyword  |WATER-Wetlands
    |                                  |column is permitted.         |
    |                                  |Spreadsheet note: Don't put  |
    |                                  |multiple keywords in the same|
    |                                  |column, add another with     |
    |                                  |ANZLICKeyword as column      |
    |                                  |header.                      |
    |----------------------------------|-----------------------------|------------------------
    |CompletenessOmission              |                             |
    |----------------------------------|-----------------------------|------------------------
    |ConceptualConsistency             |                             |
    |----------------------------------|-----------------------------|------------------------
    |NonQuantitativeAttributeAccuracy  |                             |
    |----------------------------------|-----------------------------|------------------------
    |category                          |GeoNetwork category/ies      |datasets|maps
    |                                  |"|" delimited string         |
    |                                  |Only shown in MEF, not ISO   |
    |                                  |metadata                     |
    |----------------------------------|-----------------------------|------------------------
    |custodian                         |Format is:                   |organisationName|DEWHA
    |                                  |organisationName|text\n      |positionName|Some Position
    |                                  |positionName|text\n          |voice|0262123456
    |                                  |voice|0262123456\n           |facsimile|0262123457
    |                                  |facsimile|text\n             |deliveryPoint|GPO Box 123
    |                                  |deliveryPoint|text\n         |city|Canberra
    |                                  |city|text\n                  |administrativeArea|ACT
    |                                  |administrativeArea|text\n    |postalCode|2600
    |                                  |postalCode|text\n            |country|Australia
    |                                  |country|text\n               |electronicMailAddress|example@address.gov.au
    |                                  |electronicMailAddress|text   |
    |                                  |Spreadsheet note: \n can be  |
    |                                  |entered in a cell by holding |
    |                                  |the [Alt] key and pressing   |
    |                                  [Enter]                       |
    |----------------------------------|-----------------------------|------------------------
    |distributor                       |As per custodian             |
    |----------------------------------|-----------------------------|------------------------
    |GeographicDescription             |Text describing the          |Kakadu
    |                                  |geographic location of the   |
    |                                  |image. More than one column  |
    |                                  |is permitted.                |
    |----------------------------------|-----------------------------|------------------------
    |mediaid                           |An ID code for the offline   |RSA0000001
    |                                  |media                        |
    |----------------------------------|-----------------------------|------------------------
    |mediatype                         |Must be one of:              |digitalLinearTape
    |                                  | - cdRom                     |
    |                                  | - dvd                       |
    |                                  | - digitalLinearTape         |
    |                                  |Or others listed at:         |
    |                                  |http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MediumNameCode
    |----------------------------------|-----------------------------|------------------------
    |OnlineResource                    |More than one                |URL|http://pandora:81/ecwp/ecw_wms.dll?nautical_charts?Request=GetCapabilities
    |                                  |OnlineResource column is     |protocol|OGC:WMS-1.1.1-http-get-map
    |                                  |permitted. Spreadsheet note: |name|L00676
    |                                  |Don't put multiple resources |description|Image Web Server Web Map Service
    |                                  |in the same column, add      |function|download
    |                                  |with OnlineResource as  the  |
    |                                  |column header. Format is:    |
    |                                  |URL|text\n                   |
    |                                  |protocol|text\n              |
    |                                  |name|text\n                  |
    |                                  |description|text\n           |
    |                                  |function|text                |
    |----------------------------------|-----------------------------|------------------------
    |operations                        |GeoNetwork operation/s       |view|edit|featured
    |                                  |"|" delimited string         |
    |                                  |Only shown in MEF, not ISO   |
    |                                  |metadata                     |
    |----------------------------------|-----------------------------|------------------------
    |originator                        |As per custodian             |
    |----------------------------------|-----------------------------|------------------------
    |publisher                         |As per custodian             |
    |----------------------------------|-----------------------------|------------------------
    |resourceProvider                  |As per custodian             |
    |----------------------------------|-----------------------------|------------------------
    |scale                             |representative fraction      |25000 (represents 1:25,000)
    |                                  |denominator                  |
    |                                  |(MUST be an integer)         |
    |----------------------------------|-----------------------------|------------------------
  Note: see this U{thread<http://n2.nabble.com/Re-metadata-Official-way-of-representing-OGC-services-in-ISO-19139-metadata-protocol-element-SEC-UNC-td3463929.html>}
  regarding OnlineResource URL protocol syntax

@todo: Should XSL files be described by a .py instead of a .xml file?
       That way they could be imported automatically and additional metadata elements
       could be documented there instead of above here...
'''
from glob import glob as _glob
from os import path as _path, environ as _env
import StringIO as _strio
import time as _time,os as _os,zipfile as _zip,shutil as _sh,sys as _sys,tempfile as _tmp
if __name__ == '__main__':_sys.exit(0)

from lxml import etree as _etree
from metageta import utilities  as _utilities, __path__ as _mpath
#from metageta import

#++++++++++++++++++++++++
#Public vars
#++++++++++++++++++++++++
transforms={}
'''Pre-defined XSL transforms'''

xslfiles={}
'''Pre-defined XSL files'''

#++++++++++++++++++++++++
#Initialise pub/priv properties
#++++++++++++++++++++++++
#load known XSL transforms
for _f in _glob(_path.join(__path__[0],'*.xml')):
    #_xml=_Parse('file:%s'%_f)
    _xml=_etree.parse(_f)
    _name = str(_xml.xpath('string(/stylesheet/@name)'))
    _file = str(_xml.xpath('string(/stylesheet/@file)'))
    _desc = str(_xml.xpath('string(/stylesheet/@description)'))
    xslfiles[_name]=_file
    transforms[_name]=_desc

#Load config
config=_etree.parse('%s/config/config.xml'%_mpath[0])
categories={'default':config.xpath('string(/config/geonetwork/categories/@default)'),
             'categories':config.xpath('/config/geonetwork/categories/category/@name')
             }
if not categories['default'] and not categories['categories']:categories={'default': 'datasets', 'categories': ['datasets']}

operations={'default':config.xpath('string(/config/geonetwork/operations/@default)'),
             'operations':config.xpath('/config/geonetwork/operations/operation/@name')
             }
if not operations['default'] and not operations['operations']:operations={'default': 'view', 'operations': ['view','editing','dynamic','featured']}

site={}
for _key in ['name','organization','siteId']:
    _s=config.xpath('string(/config/geonetwork/site/%s)'%_key)
    if _s:site[_key]=_s
    else:site[_key]='dummy'

#++++++++++++++++++++++++
#Public methods
#++++++++++++++++++++++++
# def Transform(inxmlstring,transform,outxmlfile):
#     '''
#     Transform a metadata record to XML using an XSL stylesheet
#
#     @param inxmlstring: metadata record in XML format.
#     @param transform: may be one of the pre-defined XSL transforms or a path to a custom XSL file.
#     @param outxmlfile: File to write transformed metadata to.
#     '''
#     if xslfiles.has_key(transform): #Is it a known XSL transform...?
#         xslfile = _path.join(__path__[0],xslfiles[transform]).replace('\\','/')
#     elif _path.exists(transform):    #Have we been passed an XSL file path...?
#         xslfile=_path.abspath(transform).replace('\\','/') #Xslt.Transform doesn't like backslashes in absolute paths...
#     else: raise ValueError, 'Can not transform using %s!' % transform
#     xsl = _etree.parse(xslfile)
#     xml = _etree.fromstring(inxmlstring)
#     xslt = _etree.XSLT(xsl)
#     try:
#         result = xslt(xml)
#     except:
#         raise RuntimeError(xslt.error_log)
#
#     print xslt.error_log
#     open(outxmlfile, 'w').write(str(result))

class Transform(object):
    '''
    Transform a metadata record to XML using an XSL stylesheet

    @param inxmlstring: metadata record in XML format.
    @param transform: may be one of the pre-defined XSL transforms or a path to a custom XSL file.
    @param outxmlfile: File to write transformed metadata to.
    '''
    def __init__(self,transform):
        '''
        Transform a metadata record to XML using an XSL stylesheet

        @param transform: may be one of the pre-defined XSL transforms or a path to a custom XSL file.
        '''
        if xslfiles.has_key(transform): #Is it a known XSL transform...?
            xslfile = _path.join(__path__[0],xslfiles[transform]).replace('\\','/')
        elif _path.exists(transform):    #Have we been passed an XSL file path...?
            xslfile=_path.abspath(transform).replace('\\','/') #Xslt.Transform doesn't like backslashes in absolute paths...
        else: raise ValueError, 'Can not transform using %s!' % transform
        xsl = _etree.parse(xslfile)
        self.xslt = _etree.XSLT(xsl)

    def transform(self, inxmlstring, outxmlfile):
        '''
        Transform a metadata record to XML using an XSL stylesheet

        @param inxmlstring: metadata record in XML format.
        @param outxmlfile: File to write transformed metadata to.
        '''
        xml = _etree.fromstring(inxmlstring)
        result = self.xslt(xml)
        open(outxmlfile, 'w').write(str(result))
        return self.xslt.error_log

def ListToXML(lst,root,asstring=True):
    '''Transform a metadata record to a flat XML string'''

    root = _etree.Element(root)

    for fld in lst:
        col=fld[0]
        dat=fld[1]

        if type(dat) is unicode:
            dat=dat.encode('ascii','xmlcharrefreplace')
        elif type(dat) is str:
            dat=dat.decode(_utilities.encoding).encode('ascii','xmlcharrefreplace')
        else:dat=str(dat)

        child=_etree.SubElement(root,col)
        child.text=dat

    if asstring:return _etree.tostring(root)
    else:return root

def DictToXML(dic,root,asstring=True):
    '''Transform a metadata record to a flat XML string'''

    root = _etree.Element(root)

    for col in dic:
        dat=dic[col]
        if type(dat) is unicode:
            dat=dat.encode('ascii','xmlcharrefreplace')
        elif type(dat) is str:
            dat=dat.decode(_utilities.encoding).encode('ascii','xmlcharrefreplace')
        else:dat=str(dat)

        child=_etree.SubElement(root,col)
        child.text=dat

    if asstring:return _etree.tostring(root)
    else:return root


def CreateMEF(outdir,xmlfile,uid,overviews=[],cat=categories['default'],ops=operations['default']):
    '''Generate Geonetwork "Metadata Exchange Format" from an ISO19139 XML record

    @see:

        U{http://www.fao.org/geonetwork/docs/ch17s02.html}

        U{http://trac.osgeo.org/geonetwork/wiki/MEF}

    @param outdir: Directory to write MEF file to.
    @param xmlfile: XML file to create MEF from.
    @param uid: ID of metadata record (UUID/GUID string).
    @keyword overviews: List of overview image file (e.g quicklooks & thumbnails) OPTIONAL.
    @keyword cat: List of GeoNetwork categories to include in the MEF OPTIONAL.

    @todo: Assumes metadata is ISO19139, need to make generic somehow...

    '''

    xmldir=_path.dirname(xmlfile)
    curdir=_path.abspath(_os.curdir)
    #mefdir=_path.join(_os.environ['TEMP'],_path.basename(_path.splitext(xmlfile)[0]))
    mefdir=mefdir=_tmp.mkdtemp()
    mefpath='%s.mef'%(_path.join(outdir,_path.basename(_path.splitext(xmlfile)[0])))
    try: #
        if _path.exists(mefpath):_os.remove(mefpath)
        #if _path.exists(mefdir):_sh.rmtree(mefdir)
        mef=_zip.ZipFile(mefpath,'w',_zip.ZIP_DEFLATED)
        #_os.mkdir(mefdir)
        _os.chdir(mefdir)
        _sh.copy(xmlfile,'metadata.xml')
        if overviews:
            _os.mkdir('public')
            for f in overviews:
                _sh.copy(f,_path.join('public',_path.basename(f)))
        _CreateInfo(uid,overviews,cat,ops)
        #_sh.copy(xmlfile,'metadata.xml')
        for f in _utilities.rglob('.'):
            if not _path.isdir(f): mef.write(f)
    finally:
        try:_os.chdir(curdir)
        except:pass
        try:
            mef.close()
            del mef
        except:pass
        try:_sh.rmtree(mefdir)
        except:pass
#++++++++++++++++++++++++
#Private methods
#++++++++++++++++++++++++
def _CreateInfo(uid,overviews=[],cat=categories['default'],ops=operations['default']):
    '''Create MEF info.xml file'''
    now = _time.strftime('%Y-%m-%dT%H:%M:%S',_time.localtime())
    if overviews:format='partial'
    else:format='simple'

    general=[('createDate',now),('changeDate',now),
             ('schema','iso19139'),('isTemplate','false'),
             ('localId',''),('format',format),
             ('rating','0'),('popularity','2'),
             ('uuid',uid),('siteId',site['siteId']),('siteName',site['name'])]

    root = _etree.Element('info')
    root.set('version','1.1')

    #General
    parent=_etree.SubElement(root,'general')
    for key in general:
        child=_etree.SubElement(parent,key[0])
        child.text=key[1]

    #Categories
    parent=_etree.SubElement(root,'categories')
    for c in cat.split('|'):
        child=_etree.SubElement(parent,'category')
        child.set('name',c)

    #Operations
    parent=_etree.SubElement(root,'privileges')
    child=_etree.SubElement(parent,'group')
    child.set('name','all')
    for op in ops.split('|'):
        sub=_etree.SubElement(child, 'operation')
        sub.set('name',op)

    #Public
    if overviews:
        parent=_etree.SubElement(root,'public')
        for f in overviews:
            child=_etree.SubElement(parent,'file')
            child.set('name',_path.basename(f))
            child.set('changeDate',_time.strftime('%Y-%m-%dT%H:%M:%S', _time.localtime(_path.getmtime(f))))

        parent=_etree.SubElement(root,'private')

    #_Dom.PrettyPrint(doc,open('info.xml','w'))
    open('info.xml', 'w').write(_etree.tostring(root))
