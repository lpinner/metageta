# -*- coding: latin-1 -*-
# Copyright (c) 2009 Australian Government, Department of Environment, Heritage, Water and the Arts
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
    |lineage                           |                             |                           
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
    |originator                        |As per custodian             |                           
    |----------------------------------|-----------------------------|------------------------
    |publisher                         |As per custodian             |                           
    |----------------------------------|-----------------------------|------------------------
    |resourceProvider                  |As per custodian             |                           
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
import os.path as _path
import StringIO as _strio
import time as _time,os as _os,zipfile as _zip,shutil as _sh,sys as _sys
if __name__ == '__main__':_sys.exit(0)

from Ft.Xml.Xslt import Transform as _Transform
from Ft.Xml import Parse as _Parse
from Ft.Xml import Domlette as _Dom

import utilities  as _utilities

#++++++++++++++++++++++++
#Public vars
#++++++++++++++++++++++++
transforms={}
'''Pre-defined XSL transforms'''

xslfiles={}
'''Pre-defined XSL files'''

#++++++++++++++++++++++++
#Initialise pub/priv properties - load known XSL transforms
#++++++++++++++++++++++++
for _f in _glob(_path.join(__path__[0],'*.xml')):
    _xml=_Parse('file:%s'%_f)
    _name = str(_xml.xpath('string(/stylesheet/@name)'))
    _file = str(_xml.xpath('string(/stylesheet/@file)'))
    _desc = str(_xml.xpath('string(/stylesheet/@description)'))
    xslfiles[_name]=_file
    transforms[_name]=_desc
    del _xml

#++++++++++++++++++++++++
#Public methods    
#++++++++++++++++++++++++
def Transform(inxmlstring,transform,outxmlfile):
    '''
    Transform a metadata record to XML using an XSL stylesheet
    
    @param inxmlstring: metadata record in XML format.
    @param transform: may be one of the pre-defined XSL transforms or a path to a custom XSL file.
    @param outxmlfile: File to write transformed metadata to.
    '''
    if xslfiles.has_key(transform): #Is it a known XSL transform...?
        xslfile = _path.join(__path__[0],xslfiles[transform]).replace('\\','/')
    elif _path.exists(transform):    #Have we been passed an XSL file path...?
        xslfile=_path.abspath(transform).replace('\\','/') #Xslt.Transform doesn't like backslashes in absolute paths...
    else: raise ValueError, 'Can not transform using %s!' % transform
    result = _Transform(inxmlstring, 'file:///'+xslfile, output=open(outxmlfile, 'w'))

def DictToXML(dic,root):
    '''Transform a metadata record to a flat XML string'''
    doc=_Dom.implementation.createRootNode('file:///%s.xml'%root)
    docelement = doc.createElementNS(None, root)
    for col in dic:
        dat=dic[col]
        if type(dat) is unicode:
            dat=dat.encode('ascii','xmlcharrefreplace')
        elif type(dat) is str:
            dat=dat.decode(_utilities.encoding).encode('ascii','xmlcharrefreplace')
        else:dat=str(dat)
        child=doc.createElementNS(None, col)
        text=doc.createTextNode(dat)
        child.appendChild(text)
        docelement.appendChild(child)

    doc.appendChild(docelement)
    buf=_strio.StringIO()
    _Dom.PrettyPrint(doc,stream=buf)
    return buf.getvalue()

def ListToXML(lst,root):
    '''Transform a metadata record to a flat XML string'''
    doc=_Dom.implementation.createRootNode('file:///%s.xml'%root)
    docelement = doc.createElementNS(None, root)
    for fld in lst:
        col=fld[0]
        dat=fld[1]
        if type(dat) is unicode:
            dat=dat.encode('ascii','xmlcharrefreplace')
        elif type(dat) is str:
            dat=dat.decode(_utilities.encoding).encode('ascii','xmlcharrefreplace')
        else:dat=str(dat)
        child=doc.createElementNS(None, col)
        text=doc.createTextNode(dat)
        child.appendChild(text)
        docelement.appendChild(child)

    doc.appendChild(docelement)
    buf=_strio.StringIO()
    _Dom.PrettyPrint(doc,stream=buf)
    return buf.getvalue()

def CreateMEF(outdir,xmlfile,uid,overviews=[]):
    '''Generate Geonetwork "Metadata Exchange Format" from an ISO19139 XML record
    
    @see:
        
        U{http://www.fao.org/geonetwork/docs/ch17s02.html}
        
        U{http://trac.osgeo.org/geonetwork/wiki/MEF}
    
    @param outdir: Directory to write MEF file to.
    @param xmlfile: XML file to create MEF from.
    @param uid: ID of metadata record (UUID/GUID string).
    @keyword overviews: List of overview image file (e.g quicklooks & thumbnails) OPTIONAL.

    @todo: Assumes metadata is ISO19139, need to make generic somehow...

    '''
    xmldir=_path.dirname(xmlfile)
    curdir=_path.abspath(_os.curdir)
    mefdir=_path.join(_os.environ['TEMP'],_path.basename(_path.splitext(xmlfile)[0]))
    mefpath='%s.mef'%(_path.join(outdir,_path.basename(_path.splitext(xmlfile)[0])))
    #mefdir=_path.splitext(xmlfile)[0]) #to get around 260 char filename limit...
    #mefpath='%s.mef'%(mefdir)
    try:
        if _path.exists(mefpath):_os.remove(mefpath)
        if _path.exists(mefdir):_sh.rmtree(mefdir)
        mef=_zip.ZipFile(mefpath,'w',_zip.ZIP_DEFLATED)
        _os.mkdir(mefdir)
        _os.chdir(mefdir)
        ##mef=_zip.ZipFile(r'%s.mef'%(uid),'w',_zip.ZIP_DEFLATED)
        ##_os.mkdir(uid)
        ##_os.chdir(uid)
        _sh.copy(xmlfile,'metadata.xml')
        if overviews:
            _os.mkdir('public')
            for f in overviews:
                _sh.copy(f,_path.join('public',_path.basename(f)))
        _CreateInfo(uid,overviews)
        _sh.copy(xmlfile,'metadata.xml')
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
def _CreateInfo(uid,overviews=[]):
    '''Create MEF info.xml file'''
    now = _time.strftime('%Y-%m-%dT%H:%M:%S',_time.localtime())
    if overviews:format='partial'
    else:format='simple'

    general={'createDate':now,'changeDate':now,
             'schema':'iso19139','isTemplate':'false',
             'format':format,'uuid':uid,
             'siteId':'dummy','siteName':'dummy',
             'localId':'','rating':'0','popularity':'2'}

    privileges = ['view','editing','dynamic','featured']

    doc=_Dom.implementation.createRootNode('file:///info.xml')
    root = doc.createElementNS(None, 'info')
    root.setAttributeNS(None, 'version','1.1')

    #General
    parent=doc.createElementNS(None, 'general')
    for key in general:
        child=doc.createElementNS(None, key)
        text=doc.createTextNode(general[key])
        child.appendChild(text)
        parent.appendChild(child)
    root.appendChild(parent)

    #Categories
    parent=doc.createElementNS(None, 'categories')
    child=doc.createElementNS(None, 'category')
    child.setAttributeNS(None, 'name','datasets')
    parent.appendChild(child)
    root.appendChild(parent)

    parent=doc.createElementNS(None, 'privileges')
    child=doc.createElementNS(None, 'group')
    child.setAttributeNS(None, 'name','all')
    for op in privileges:
        sub=doc.createElementNS(None, 'operation')
        sub.setAttributeNS(None, 'name',op)
        child.appendChild(sub)
    parent.appendChild(child)
    root.appendChild(parent)

    #Public
    if overviews:
        parent=doc.createElementNS(None, 'public')
        for f in overviews:
            child=doc.createElementNS(None, 'file')
            child.setAttributeNS(None, 'name',_path.basename(f))
            child.setAttributeNS(None, 'changeDate',_time.strftime('%Y-%m-%dT%H:%M:%S', _time.localtime(_path.getmtime(f))))
            parent.appendChild(child)
        root.appendChild(parent)

        parent=doc.createElementNS(None, 'private')
        root.appendChild(parent)

    doc.appendChild(root)
    _Dom.PrettyPrint(doc,open('info.xml','w'))
