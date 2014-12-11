<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"   
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
  xmlns:fn="http://www.w3.org/2005/xpath-functions" 
  xmlns:xdt="http://www.w3.org/2005/xpath-datatypes" 
  xmlns:gco="http://www.isotc211.org/2005/gco" 
  xmlns:gmd="http://www.isotc211.org/2005/gmd" 
  xmlns:xlink="http://www.w3.org/1999/xlink" 
  xmlns:gts="http://www.isotc211.org/2005/gts" 
  xmlns:gsr="http://www.isotc211.org/2005/gsr" 
  xmlns:gss="http://www.isotc211.org/2005/gss" 
  xmlns:gmx="http://www.isotc211.org/2005/gmx" 
  xmlns:gml="http://www.opengis.net/gml" 
  xsi:schemaLocation="http://www.isotc211.org/2005/gmd http://www.isotc211.org/2005/gmd/gmd.xsd"
  xmlns:func="http://exslt.org/functions"
  xmlns:exsl="http://exslt.org/common"
  xmlns:str="http://exslt.org/strings"
  xmlns:date="http://exslt.org/dates-and-times"
  xmlns:math="http://exslt.org/math"
  extension-element-prefixes="str func exsl date math">

  <xsl:import href="date.format-date.function.xsl" />
  
  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:param name="hierarchyLevel" select="'dataset'"/>
  <xsl:param name="themesListLocation" select="'http://asdd.ga.gov.au/asdd/profileinfo/anzlic-theme.xml'"/><!-- Change this to canonical location when available -->
  <xsl:param name="codesListLocation" select="'http://asdd.ga.gov.au/asdd/profileinfo/'"/><!-- Change this to canonical location when available -->
  <xsl:param name="metadataOrganisation" select="'metadataOrganisation'"/><!-- no default -->
  <xsl:param name="topicCategory"  select="'imageryBaseMapsEarthCover'"/>
  <xsl:param name="resourceCreationDate" /><!-- no default -->
  <xsl:variable name="hierarchyLevelName">
    <xsl:choose><xsl:when test="$hierarchyLevel='dataset'">Dataset</xsl:when><xsl:otherwise><xsl:value-of select="$hierarchyLevel"/></xsl:otherwise></xsl:choose>
  </xsl:variable>
  <xsl:variable 
            name="config"
            select="document('../config/config.xml')/config"/>
    
  <xsl:template match="/crawlresult">
    <gmd:MD_Metadata xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                     xmlns:fn="http://www.w3.org/2005/xpath-functions" 
                     xmlns:xdt="http://www.w3.org/2005/xpath-datatypes" 
                     xmlns:gco="http://www.isotc211.org/2005/gco" 
                     xmlns:gmd="http://www.isotc211.org/2005/gmd" 
                     xmlns:xlink="http://www.w3.org/1999/xlink" 
                     xmlns:gts="http://www.isotc211.org/2005/gts" 
                     xmlns:gsr="http://www.isotc211.org/2005/gsr" 
                     xmlns:gss="http://www.isotc211.org/2005/gss" 
                     xmlns:gmx="http://www.isotc211.org/2005/gmx" 
                     xmlns:gml="http://www.opengis.net/gml" 
                     xsi:schemaLocation="http://www.isotc211.org/2005/gmd http://www.isotc211.org/2005/gmd/gmd.xsd">
      <xsl:if test="normalize-space(DELETED) = '1'">>
        <xsl:message terminate="yes">
          <xsl:value-of select="normalize-space(filename)"/> has been marked as deleted, XSLT processing will be terminated.
        </xsl:message>
      </xsl:if>
      <gmd:fileIdentifier>
        <gco:CharacterString><xsl:value-of select="guid"/></gco:CharacterString>
      </gmd:fileIdentifier>
      <gmd:language>
        <gco:CharacterString>eng</gco:CharacterString>
      </gmd:language>
      <gmd:characterSet>
        <gmd:MD_CharacterSetCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
      </gmd:characterSet>
      <xsl:if test="normalize-space(parentIdentifier)">
        <gmd:parentIdentifier>
          <gco:CharacterString><xsl:value-of select="parentIdentifier"/></gco:CharacterString>
        </gmd:parentIdentifier>
      </xsl:if>
      <xsl:choose>
          <xsl:when test="normalize-space(hierarchyLevel)">
        <gmd:CI_RoleCode>
          <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode</xsl:attribute>
          <xsl:attribute name="codeListValue"><xsl:value-of select="$contact"/></xsl:attribute>
          <xsl:value-of select="$contact"/>
        </gmd:CI_RoleCode>
            <gmd:hierarchyLevel>
              <gmd:MD_ScopeCode>
                <xsl:attribute name="codeList">http://asdd.ga.gov.au/asdd/profileinfo/GAScopeCodeList.xml#MD_ScopeCode</xsl:attribute>
                <xsl:attribute name="codeListValue"><xsl:value-of select="$hierarchyLevel"/></xsl:attribute>
                <xsl:value-of select="$hierarchyLevel"/>
              </gmd:MD_ScopeCode>
            </gmd:hierarchyLevel>
            <gmd:hierarchyLevelName>
              <gco:CharacterString><xsl:value-of select="$hierarchyLevel"/></gco:CharacterString>
            </gmd:hierarchyLevelName>
          </xsl:when>
          <xsl:otherwise>
            <gmd:hierarchyLevel>
              <gmd:MD_ScopeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/GAScopeCodeList.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
            </gmd:hierarchyLevel>
            <gmd:hierarchyLevelName>
              <gco:CharacterString>dataset</gco:CharacterString>
            </gmd:hierarchyLevelName>
          </xsl:otherwise>
      </xsl:choose>
      <gmd:contact>
        <xsl:call-template name="default_contact">
          <xsl:with-param name="contact" select="'publisher'"/>
        </xsl:call-template>
      </gmd:contact>
      <gmd:dateStamp>
          <gco:Date>
              <xsl:choose>
                  <xsl:when test="normalize-space(metadatadate)">
                      <xsl:choose>
                          <xsl:when test="contains(metadatadate,'T')">
                            <xsl:value-of select="str:split(metadatadate,'T')[1]"/><!--date doesn't validate with time values-->
                          </xsl:when>
                          <xsl:otherwise><xsl:value-of select="metadatadate"/></xsl:otherwise>
                      </xsl:choose>
                  </xsl:when>
                  <xsl:otherwise><xsl:value-of select="date:format-date(date:date-time(),'yyyy-MM-dd')"/></xsl:otherwise>
              </xsl:choose>
          </gco:Date>
      </gmd:dateStamp>
      <gmd:metadataStandardName>
        <gco:CharacterString>ANZLIC Metadata Profile: An Australian/New Zealand Profile of AS/NZS ISO 19115:2005, Geographic information - Metadata</gco:CharacterString>
      </gmd:metadataStandardName>
      <gmd:metadataStandardVersion>
         <gco:CharacterString>1.1</gco:CharacterString>
      </gmd:metadataStandardVersion>
      
      <xsl:call-template name="referenceSystemInfo"/>
      <!--xsl:call-template name="metadataExtensionInfo"/-->
      <xsl:call-template name="identificationInfo"/>
      <xsl:call-template name="contentInfo"/>
      <xsl:call-template name="distributionInfo"/>
 
      <gmd:dataQualityInfo>
        <gmd:DQ_DataQuality>
          <gmd:scope>
            <gmd:DQ_Scope>
              <gmd:level>
                <gmd:MD_ScopeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
              </gmd:level>
            </gmd:DQ_Scope>
          </gmd:scope>
          <xsl:call-template name="dataQualityInfo">
            <xsl:with-param name="DQ_Type">CompletenessOmission</xsl:with-param>
            <xsl:with-param name="DQ_Value" select="CompletenessOmission"/>
          </xsl:call-template>
          <xsl:call-template name="dataQualityInfo">
            <xsl:with-param name="DQ_Type">AbsoluteExternalPositionalAccuracy</xsl:with-param>
            <xsl:with-param name="DQ_Value" select="AbsoluteExternalPositionalAccuracy"/>
          </xsl:call-template>
          <xsl:call-template name="dataQualityInfo">
            <xsl:with-param name="DQ_Type">ConceptualConsistency</xsl:with-param>
            <xsl:with-param name="DQ_Value" select="ConceptualConsistency"/>
          </xsl:call-template>
          <xsl:call-template name="dataQualityInfo">
            <xsl:with-param name="DQ_Type">NonQuantitativeAttributeAccuracy</xsl:with-param>
            <xsl:with-param name="DQ_Value" select="NonQuantitativeAttributeAccuracy"/>
          </xsl:call-template>
          <xsl:call-template name="dataQualityInfo">
            <xsl:with-param name="DQ_Type">lineage</xsl:with-param>
            <xsl:with-param name="DQ_Value" select="lineage"/>
          </xsl:call-template>
        </gmd:DQ_DataQuality>
      </gmd:dataQualityInfo>
      <xsl:call-template name="metadataConstraints"/>
    </gmd:MD_Metadata>
  </xsl:template>

  <!--
    TOP LEVEL TEMPLATES
  -->
  <xsl:template name="contact">
    <gmd:pointOfContact>
      <xsl:choose>
        <xsl:when test="normalize-space(custodian)">
          <xsl:variable name="other_contacts"> <!-- Test for any other contacts-->
            <!-- http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode -->
            <xsl:element name="custodian"><xsl:value-of select="custodian"/></xsl:element>
          </xsl:variable>
          <xsl:call-template name="other_contact">
            <xsl:with-param name="contactinfo" select="exsl:node-set($other_contacts)/*"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
            <xsl:call-template name="default_contact"/>
        </xsl:otherwise>
      </xsl:choose>
    </gmd:pointOfContact><!--/gmd:pointOfContact-->
    <xsl:variable name="other_contacts"> <!-- Test for any other contacts-->
      <!-- http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode -->
      <xsl:element name="creator"><xsl:value-of select="creator"/></xsl:element>
      <xsl:element name="owner"><xsl:value-of select="owner"/></xsl:element>
      <xsl:element name="user"><xsl:value-of select="user"/></xsl:element>
      <xsl:element name="resourceProvider"><xsl:value-of select="resourceProvider"/></xsl:element>
      <xsl:element name="distributor"><xsl:value-of select="distributor"/></xsl:element>
      <xsl:element name="originator"><xsl:value-of select="originator"/></xsl:element>
      <xsl:element name="publisher"><xsl:value-of select="publisher"/></xsl:element>
      <xsl:element name="pointOfContact"><xsl:value-of select="pointOfContact"/></xsl:element>
      <xsl:element name="principalInvestigator"><xsl:value-of select="principalInvestigator"/></xsl:element>
      <xsl:element name="processor"><xsl:value-of select="processor"/></xsl:element>
      <xsl:element name="author"><xsl:value-of select="author"/></xsl:element>
    </xsl:variable>
    <xsl:for-each select="exsl:node-set($other_contacts)/*">
      <xsl:if test="normalize-space(.)">
        <gmd:pointOfContact>
          <xsl:call-template name="other_contact">
            <xsl:with-param name="contactinfo" select="."/>
          </xsl:call-template>
        </gmd:pointOfContact><!--/gmd:pointOfContact-->
      </xsl:if>
    </xsl:for-each>
  </xsl:template><!--contact-->
  <xsl:template name="default_contact">
    <xsl:param name="contact">custodian</xsl:param> <!--default-->
    <!--xsl:variable 
      name="defaultcontact"
      select="document('../config/config.xml')/config/defaultcontact"/-->
    <xsl:variable 
      name="defaultcontact"
      select="$config/defaultcontact"/>
        
    <gmd:CI_ResponsibleParty>
      <gmd:individualName gco:nilReason="withheld">
        <gco:CharacterString>
        </gco:CharacterString>
      </gmd:individualName>
      <gmd:organisationName>
        <gco:CharacterString><xsl:value-of select="$defaultcontact/organisation"/></gco:CharacterString>
      </gmd:organisationName>
      <gmd:positionName>
        <gco:CharacterString><xsl:value-of select="$defaultcontact/position"/></gco:CharacterString>
      </gmd:positionName>
      <gmd:contactInfo>
        <gmd:CI_Contact>
             <gmd:phone>
                <gmd:CI_Telephone>
                   <gmd:voice>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/telephone"/></gco:CharacterString>
                   </gmd:voice>
                   <gmd:facsimile>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/facsimile"/></gco:CharacterString>
                   </gmd:facsimile>
                </gmd:CI_Telephone>
             </gmd:phone>
             <gmd:address>
                <gmd:CI_Address>
                   <gmd:deliveryPoint>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/address/deliveryPoint"/></gco:CharacterString>
                   </gmd:deliveryPoint>
                   <gmd:city>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/address/city"/></gco:CharacterString>
                   </gmd:city>
                   <gmd:administrativeArea>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/address/administrativeArea"/></gco:CharacterString>
                   </gmd:administrativeArea>
                   <gmd:postalCode>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/address/postalCode"/></gco:CharacterString>
                   </gmd:postalCode>
                   <gmd:country>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/address/country"/></gco:CharacterString>
                   </gmd:country>
                   <gmd:electronicMailAddress>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/emailAddress"/></gco:CharacterString>
                   </gmd:electronicMailAddress>
                </gmd:CI_Address>
             </gmd:address>
             <gmd:onlineResource> <!--ANZMet Lite strips this out...-->
                <gmd:CI_OnlineResource>
                   <gmd:linkage>
                      <gmd:URL><xsl:value-of select="$defaultcontact/onlineResource/URL"/></gmd:URL>
                   </gmd:linkage>
                   <gmd:protocol>
                      <gco:CharacterString>HTTP</gco:CharacterString>
                   </gmd:protocol>
                   <gmd:description>
                      <gco:CharacterString><xsl:value-of select="$defaultcontact/onlineResource/description"/></gco:CharacterString>
                   </gmd:description>
                </gmd:CI_OnlineResource>
             </gmd:onlineResource>
          </gmd:CI_Contact>
      </gmd:contactInfo>
      <gmd:role>
        <gmd:CI_RoleCode>
          <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode</xsl:attribute>
          <xsl:attribute name="codeListValue"><xsl:value-of select="$contact"/></xsl:attribute>
          <xsl:value-of select="$contact"/>
        </gmd:CI_RoleCode>
      </gmd:role>    
    </gmd:CI_ResponsibleParty>
  </xsl:template><!--default_contact-->
  <xsl:template name="other_contact">
    <xsl:param name="contactinfo"/>
    <xsl:variable name="contact" select="str:toNode($contactinfo)"/>
    <gmd:CI_ResponsibleParty>
      <gmd:individualName gco:nilReason="withheld">
        <gco:CharacterString>
        </gco:CharacterString>
      </gmd:individualName>
      <gmd:organisationName>
        <gco:CharacterString><xsl:value-of select="$contact/organisationName"/></gco:CharacterString>
      </gmd:organisationName>
      <gmd:positionName>
        <gco:CharacterString><xsl:value-of select="$contact/positionName"/></gco:CharacterString>
      </gmd:positionName>
      <gmd:contactInfo>
        <gmd:CI_Contact>
           <gmd:phone>
              <gmd:CI_Telephone>
                 <gmd:voice>
                   <gco:CharacterString><xsl:value-of select="$contact/voice"/></gco:CharacterString>
                 </gmd:voice>
                 <gmd:facsimile>
                   <gco:CharacterString><xsl:value-of select="$contact/facsimile"/></gco:CharacterString>
                 </gmd:facsimile>
              </gmd:CI_Telephone>
           </gmd:phone>
           <gmd:address>
             <gmd:CI_Address>
               <gmd:deliveryPoint>
                 <gco:CharacterString><xsl:value-of select="$contact/deliveryPoint"/></gco:CharacterString>
               </gmd:deliveryPoint>
               <gmd:city>
                 <gco:CharacterString><xsl:value-of select="$contact/city"/></gco:CharacterString>
               </gmd:city>
               <gmd:administrativeArea>
                   <gco:CharacterString><xsl:value-of select="$contact/administrativeArea"/></gco:CharacterString>
                </gmd:administrativeArea>
                <gmd:postalCode>
                    <gco:CharacterString><xsl:value-of select="$contact/postalCode"/></gco:CharacterString>
                </gmd:postalCode>
                <gmd:country>
                  <gco:CharacterString><xsl:value-of select="$contact/country"/></gco:CharacterString>
                </gmd:country>
                <gmd:electronicMailAddress>
                  <gco:CharacterString><xsl:value-of select="$contact/electronicMailAddress"/></gco:CharacterString>
                </gmd:electronicMailAddress>
              </gmd:CI_Address>
           </gmd:address>
        </gmd:CI_Contact>
      </gmd:contactInfo>
      <gmd:role>
        <gmd:CI_RoleCode>
          <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode</xsl:attribute>
          <xsl:attribute name="codeListValue"><xsl:value-of select="local-name($contactinfo)"/></xsl:attribute>
          <xsl:value-of select="local-name($contactinfo)"/>
        </gmd:CI_RoleCode>
      </gmd:role>
    </gmd:CI_ResponsibleParty>
  </xsl:template><!--other_contact--> 
  <!--
  -->  
  <xsl:template name="referenceSystemInfo">
    <xsl:if test="normalize-space(srs)">
      <gmd:referenceSystemInfo>
        <gmd:MD_ReferenceSystem>
          <gmd:referenceSystemIdentifier>
            <gmd:RS_Identifier>
              <gmd:authority>
                <gmd:CI_Citation>
                <xsl:variable name="rs_type">
                  <xsl:choose>
                    <xsl:when test="not(normalize-space(epsg))">OGC</xsl:when>
                    <xsl:when test="normalize-space(epsg) = '0'">OGC</xsl:when>
                    <xsl:otherwise>EPSG</xsl:otherwise>
                  </xsl:choose>
                </xsl:variable>
                <gmd:title>
                  <gco:CharacterString>
                  <xsl:choose>
                    <xsl:when test="$rs_type='OGC'">
                    <xsl:value-of select="'OGC Well-Known Text (WKT) Representation of Spatial Reference Systems'"/>
                    </xsl:when>
                    <xsl:otherwise>
                    <xsl:value-of select="'EPSG Geodetic Parameter Dataset'"/>
                    </xsl:otherwise>
                  </xsl:choose>
                  </gco:CharacterString>
                </gmd:title>
                <gmd:date>
                  <gmd:CI_Date>
                  <gmd:date>
                    <xsl:choose>
                    <xsl:when test="$rs_type='OGC'">
                      <gco:Date>2006-10-05</gco:Date>
                    </xsl:when>
                    <xsl:otherwise>
                      <gco:Date>2007-07-16</gco:Date>
                    </xsl:otherwise>
                    </xsl:choose>
                  </gmd:date>
                  <gmd:dateType>
                    <gmd:CI_DateTypeCode>
                    <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/Codelist/gmxCodelist.xml#CI_DateTypeCode</xsl:attribute>
                    <xsl:attribute name="codeListValue">revision</xsl:attribute>
                    </gmd:CI_DateTypeCode>
                  </gmd:dateType>
                  </gmd:CI_Date>
                </gmd:date>
                <gmd:edition>
                  <xsl:choose>
                  <xsl:when test="$rs_type='OGC'">
                    <gco:CharacterString>Version 1.20</gco:CharacterString>
                  </xsl:when>
                  <xsl:otherwise>
                    <gco:CharacterString>Version 6.13</gco:CharacterString>
                  </xsl:otherwise>
                  </xsl:choose>
                </gmd:edition>
                </gmd:CI_Citation>
              </gmd:authority>
              <gmd:code>
                <gco:CharacterString>
                  <xsl:choose>
                  <xsl:when test="not(normalize-space(epsg))">
                    <!--xsl:value-of select="srs"/-->
                    <xsl:value-of select="str:replaceNewLine(srs)"/>
                  </xsl:when>
                  <xsl:when test="normalize-space(epsg) = '0'">
                    <!--xsl:value-of select="srs"/-->
                    <xsl:value-of select="str:replaceNewLine(srs)"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="round(epsg)"/>
                  </xsl:otherwise>
                  </xsl:choose>
                </gco:CharacterString>
              </gmd:code>
            </gmd:RS_Identifier>
          </gmd:referenceSystemIdentifier>
        </gmd:MD_ReferenceSystem>
      </gmd:referenceSystemInfo>
    </xsl:if>
  </xsl:template> <!--referenceSystemInfo-->
  <!--
  -->  
  <xsl:template name="metadataExtensionInfo">
    <gmd:metadataExtensionInfo>
      <gmd:MD_MetadataExtensionInformation/>
    </gmd:metadataExtensionInfo>
  </xsl:template><!--metadataExtensionInfo-->  
  <!--
  -->  
  <xsl:template name="identificationInfo">
      <gmd:identificationInfo>
        <gmd:MD_DataIdentification>
          <gmd:citation>
            <gmd:CI_Citation>
              <gmd:title>
                <gco:CharacterString>
                  <xsl:choose>
                    <xsl:when test="normalize-space(title)">
                      <xsl:value-of select="normalize-space(title)"/>
                    </xsl:when>
                    <xsl:otherwise>
                      <!--xsl:choose>
                        <xsl:when test="normalize-space(satellite)"><xsl:value-of select="normalize-space(satellite)"/><xsl:value-of select="' '"/></xsl:when>
                        <xsl:otherwise>Unknown satellite </xsl:otherwise>
                      </xsl:choose>
                      <xsl:choose>
                        <xsl:when test="normalize-space(sensor)"><xsl:value-of select="normalize-space(sensor)"/><xsl:value-of select="' '"/></xsl:when>
                        <xsl:otherwise>Unknown sensor </xsl:otherwise>
                      </xsl:choose-->
                      <xsl:if test="normalize-space(satellite)"><xsl:value-of select="normalize-space(satellite)"/><xsl:value-of select="' '"/></xsl:if>
                      <xsl:if test="normalize-space(sensor)"><xsl:value-of select="normalize-space(sensor)"/><xsl:value-of select="' '"/></xsl:if>
                      <xsl:value-of select="normalize-space(filename)"/><xsl:value-of select="' ('"/>
                      <xsl:value-of select="str:split(cellx,',')[1]"/><!--cellx can have multiple values (e.g. ASTER & ALI) so just pick the first 1-->
                      <xsl:value-of select="normalize-space(units)"/><xsl:value-of select="')'"/>
                    </xsl:otherwise>
                  </xsl:choose>
                </gco:CharacterString>
              </gmd:title>
              <gmd:date>
                <gmd:CI_Date>
                  <gmd:date>
                    <gco:Date>
                      <xsl:choose>
                        <xsl:when test="normalize-space(imgdate)"><xsl:value-of select="str:split(str:split(imgdate, '/')[1], 'T')[1]"/></xsl:when>
                        <xsl:otherwise><xsl:value-of select="date:format-date(date:date-time(),'yyyy-MM-dd')"/></xsl:otherwise>
                      </xsl:choose>
                    </gco:Date>
                  </gmd:date>            
                  <gmd:dateType>
                    <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode" codeListValue="creation">
                      <xsl:value-of select="'creation'"/>
                    </gmd:CI_DateTypeCode>
                  </gmd:dateType>
                </gmd:CI_Date>
              </gmd:date>
            </gmd:CI_Citation>
          </gmd:citation>
          <gmd:abstract>
            <gco:CharacterString>
              <xsl:choose>
                <xsl:when test="normalize-space(abstract)">
                  <xsl:value-of select="str:replaceNewLine(abstract)"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="'PLEASE ENTER AN ABSTRACT!'"/>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="normalize-space(mediaid)">
                  &#xA;MEDIA ID:<xsl:value-of select="normalize-space(mediaid)"/>
              </xsl:if>
              <xsl:if test="normalize-space(mediatype)">
                  &#xA;MEDIA TYPE:<xsl:value-of select="normalize-space(mediatype)"/>
              </xsl:if>
            </gco:CharacterString>
          </gmd:abstract>
          <gmd:purpose gco:nilReason="missing"><gco:CharacterString/></gmd:purpose>
          <gmd:status>
            <gmd:MD_ProgressCode 
                codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode"
                codeListValue="completed"/>
          </gmd:status>
          <xsl:call-template name="contact"/>
          <gmd:resourceMaintenance>
            <gmd:MD_MaintenanceInformation>
              <gmd:maintenanceAndUpdateFrequency>
                <gmd:MD_MaintenanceFrequencyCode 
                    codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode"
                    codeListValue="notPlanned"/>
              </gmd:maintenanceAndUpdateFrequency>
            </gmd:MD_MaintenanceInformation>
          </gmd:resourceMaintenance>
              
          <xsl:variable name="baseurl">
            <xsl:choose>
              <xsl:when test="normalize-space($config/geonetwork/site/baseurl)">
                <xsl:value-of select="concat($config/geonetwork/site/baseurl,'/srv/eng/resources.get?uuid=',guid,'&amp;access=public&amp;fname=')"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="''"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
         
          <xsl:if test="normalize-space(quicklook)">
            <gmd:graphicOverview>
              <gmd:MD_BrowseGraphic>
                <gmd:fileName>
                  <gco:CharacterString>
                    <xsl:choose>
                      <xsl:when test="contains(quicklook, '\')">
                        <xsl:value-of select="normalize-space(concat($baseurl,str:split(quicklook,'\')[last()]))"/>
                      </xsl:when>
                      <xsl:when test="contains(quicklook,'/')">
                        <xsl:value-of select="normalize-space(concat($baseurl,str:split(quicklook,'/')[last()]))"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="normalize-space(concat($baseurl,quicklook))"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </gco:CharacterString>
                </gmd:fileName>
                <gmd:fileDescription>
                  <gco:CharacterString>large_thumbnail</gco:CharacterString>
                </gmd:fileDescription>
                <gmd:fileType>
                  <gco:CharacterString><xsl:value-of select="str:split(quicklook,'.')[last()]"/></gco:CharacterString>
                </gmd:fileType>
              </gmd:MD_BrowseGraphic>
            </gmd:graphicOverview>
          </xsl:if>
          <xsl:if test="normalize-space(thumbnail)">
            <gmd:graphicOverview>
              <gmd:MD_BrowseGraphic>
                <gmd:fileName>
                  <gco:CharacterString>
                    <xsl:choose>
                      <xsl:when test="contains(thumbnail, '\')">
                        <xsl:value-of select="str:split(thumbnail,'\')[last()]"/>
                      </xsl:when>
                      <xsl:when test="contains(thumbnail, '/')">
                        <xsl:value-of select="str:split(thumbnail,'/')[last()]"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="normalize-space(thumbnail)"/>
                      </xsl:otherwise>
                    </xsl:choose>
                  </gco:CharacterString>
                </gmd:fileName>
                <gmd:fileDescription>
                  <gco:CharacterString>thumbnail</gco:CharacterString>
                </gmd:fileDescription>
                <gmd:fileType>
                  <gco:CharacterString><xsl:value-of select="str:split(thumbnail,'.')[last()]"/></gco:CharacterString>
                </gmd:fileType>
              </gmd:MD_BrowseGraphic>
            </gmd:graphicOverview>
          </xsl:if>
          
          <gmd:resourceFormat>
            <gmd:MD_Format>
              <gmd:name>
                <gco:CharacterString>
                  <xsl:value-of select="normalize-space(filetype)"/>
                </gco:CharacterString>
              </gmd:name>
              <gmd:version>
                <!--gco:CharacterString>none</gco:CharacterString-->
                <gco:CharacterString>Unknown</gco:CharacterString>
              </gmd:version>
            </gmd:MD_Format>
          </gmd:resourceFormat>
          <gmd:descriptiveKeywords>
            <gmd:MD_Keywords>
              <gmd:keyword>
                <gco:CharacterString>other</gco:CharacterString>
              </gmd:keyword>
              <gmd:type>
                <gmd:MD_KeywordTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_KeywordTypeCode" codeListValue="theme">theme</gmd:MD_KeywordTypeCode>
              </gmd:type>
              <gmd:thesaurusName>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gco:CharacterString>OSDM schedule names</gco:CharacterString>
                  </gmd:title>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:Date>2008-11-10</gco:Date>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_DateTypeCode" codeListValue="revision">revision</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:edition>
                    <gco:CharacterString>Version 1.1</gco:CharacterString>
                  </gmd:edition>
                  <gmd:editionDate>
                    <gco:Date>2008-11-10</gco:Date>
                  </gmd:editionDate>
                  <gmd:identifier>
                    <gmd:MD_Identifier>
                      <gmd:code>
                        <gco:CharacterString>http://asdd.ga.gov.au/asdd/profileinfo/osdm-schedule.xml#osdm-schedule</gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmd:identifier>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>Office of Spatial Data Management</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_RoleCode" codeListValue="custodian">custodian</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                </gmd:CI_Citation>
              </gmd:thesaurusName>
            </gmd:MD_Keywords>
          </gmd:descriptiveKeywords>
          <gmd:descriptiveKeywords>
            <gmd:MD_Keywords>
              <gmd:keyword>
                <gco:CharacterString>PHOTOGRAPHY-AND-IMAGERY-Remote-Sensing</gco:CharacterString>
              </gmd:keyword>
              <gmd:keyword>
                <gco:CharacterString>PHOTOGRAPHY-AND-IMAGERY-Satellite</gco:CharacterString>
              </gmd:keyword>
              <xsl:for-each select="*[starts-with(name(),'ANZLICKeyword')]">
                <gmd:keyword>
                  <gco:CharacterString><xsl:value-of select="."/></gco:CharacterString>
                </gmd:keyword>
              </xsl:for-each>
              <gmd:type>
                <gmd:MD_KeywordTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_KeywordTypeCode" codeListValue="theme">theme</gmd:MD_KeywordTypeCode>
              </gmd:type>
              <gmd:thesaurusName>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gco:CharacterString>ANZLIC Search Words</gco:CharacterString>
                  </gmd:title>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:Date>2008-05-16</gco:Date>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_DateTypeCode" codeListValue="revision">revision</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:edition>
                    <gco:CharacterString>Version 2.1</gco:CharacterString>
                  </gmd:edition>
                  <gmd:editionDate>
                    <gco:Date>2008-05-16</gco:Date>
                  </gmd:editionDate>
                  <gmd:identifier>
                    <gmd:MD_Identifier>
                      <gmd:code>
                        <gco:CharacterString>http://asdd.ga.gov.au/asdd/profileinfo/anzlic-theme.xml#anzlic-theme</gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmd:identifier>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>ANZLIC the Spatial Information Council</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_RoleCode" codeListValue="custodian">custodian</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                </gmd:CI_Citation>
              </gmd:thesaurusName>
            </gmd:MD_Keywords>
          </gmd:descriptiveKeywords>
          <gmd:descriptiveKeywords>
            <gmd:MD_Keywords>
              <gmd:keyword>
                <gco:CharacterString>Australia</gco:CharacterString>
              </gmd:keyword>
              <gmd:type>
                <gmd:MD_KeywordTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_KeywordTypeCode" codeListValue="place">theme</gmd:MD_KeywordTypeCode>
              </gmd:type>
              <gmd:thesaurusName>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gco:CharacterString>ANZLIC Jurisdictions</gco:CharacterString>
                  </gmd:title>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:Date>2008-10-29</gco:Date>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_DateTypeCode" codeListValue="revision">revision</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:edition>
                    <gco:CharacterString>Version 2.1</gco:CharacterString>
                  </gmd:edition>
                  <gmd:editionDate>
                    <gco:Date>2008-10-29</gco:Date>
                  </gmd:editionDate>
                  <gmd:identifier>
                    <gmd:MD_Identifier>
                      <gmd:code>
                        <gco:CharacterString>http://asdd.ga.gov.au/asdd/profileinfo/anzlic-jurisdic.xml#anzlic-jurisdic</gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmd:identifier>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>ANZLIC the Spatial Information Council</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_RoleCode" codeListValue="custodian">custodian</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                </gmd:CI_Citation>
              </gmd:thesaurusName>
            </gmd:MD_Keywords>
          </gmd:descriptiveKeywords>          
          <gmd:resourceConstraints>
            <gmd:MD_LegalConstraints>
              <gmd:useLimitation>
                <gco:CharacterString>
                  <xsl:choose>
                    <xsl:when test="useConstraints">
                      <xsl:value-of select="normalize-space(useConstraints)"/>
                    </xsl:when>
                    <xsl:otherwise>Usage constraints: Internal use only.</xsl:otherwise>
                  </xsl:choose>
                </gco:CharacterString>
              </gmd:useLimitation>
              <gmd:useConstraints>
                <gmd:MD_RestrictionCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_RestrictionCode" codeListValue="restricted">restricted</gmd:MD_RestrictionCode>
              </gmd:useConstraints>
            </gmd:MD_LegalConstraints>
          </gmd:resourceConstraints>
          <gmd:resourceConstraints>
            <gmd:MD_LegalConstraints>
              <gmd:useLimitation>
                <gco:CharacterString>
                  <xsl:choose>
                    <xsl:when test="accessConstraints">
                      <xsl:value-of select="normalize-space(accessConstraints)"/>
                    </xsl:when>
                    <xsl:otherwise>Access constraints: Internal access only.</xsl:otherwise>
                  </xsl:choose>
                </gco:CharacterString>
              </gmd:useLimitation>
              <gmd:accessConstraints>
                <gmd:MD_RestrictionCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_RestrictionCode" codeListValue="restricted">restricted</gmd:MD_RestrictionCode>
              </gmd:accessConstraints>
            </gmd:MD_LegalConstraints>
          </gmd:resourceConstraints>
          <gmd:resourceConstraints>
            <gmd:MD_SecurityConstraints>
              <gmd:useLimitation>
                <gco:CharacterString>Security classification: UNCLASSIFIED</gco:CharacterString>
              </gmd:useLimitation>
              <gmd:classification>
                <gmd:MD_ClassificationCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_ClassificationCode" codeListValue="unclassified">unclassified</gmd:MD_ClassificationCode>
              </gmd:classification>
            </gmd:MD_SecurityConstraints>
          </gmd:resourceConstraints>
          <xsl:if test="license">
            <gmd:resourceConstraints>
              <gmd:MD_LegalConstraints>
                <gmd:useLimitation>
                  <gco:CharacterString>
                    <xsl:value-of select="normalize-space(license)"/>
                  </gco:CharacterString>
                </gmd:useLimitation>
                <gmd:accessConstraints>
                  <gmd:MD_RestrictionCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_RestrictionCode" codeListValue="license">license</gmd:MD_RestrictionCode>
                </gmd:accessConstraints>
              </gmd:MD_LegalConstraints>
            </gmd:resourceConstraints>
          </xsl:if>
          <!-- Scale or Resolution -->
          <xsl:choose>
            <xsl:when test="normalize-space(scale)">
              <gmd:spatialResolution>
                <gmd:MD_Resolution>
                  <gmd:equivalentScale>
                    <gmd:MD_RepresentativeFraction>
                      <gmd:denominator>
                        <gco:Integer><xsl:value-of select="floor(scale)"/></gco:Integer>
                      </gmd:denominator>
                    </gmd:MD_RepresentativeFraction>
                  </gmd:equivalentScale>
                </gmd:MD_Resolution>
              </gmd:spatialResolution>
            </xsl:when>
            <xsl:otherwise>
              <gmd:spatialResolution>
                <gmd:MD_Resolution>
                  <gmd:distance>
                    <gco:Distance>
                      <xsl:attribute name="uom"><xsl:value-of select="units"/></xsl:attribute>
                      <xsl:value-of select="str:split(cellx,',')[1]"/>
                      <!--xsl:value-of select="cellx"/--> <!--cellx can have multiple values (e.g. ASTER & ALI) so just pick the first 1-->
                    </gco:Distance>
                  </gmd:distance>
                </gmd:MD_Resolution>
              </gmd:spatialResolution>
              <gmd:spatialResolution>
                <gmd:MD_Resolution>
                  <gmd:distance>
                    <gco:Distance>
                      <xsl:attribute name="uom"><xsl:value-of select="units"/></xsl:attribute>
                      <xsl:value-of select="str:split(celly,',')[1]"/>
                      <!--xsl:value-of select="celly"/--> <!--cellx can have multiple values (e.g. ASTER & ALI) so just pick the first 1-->
                    </gco:Distance>
                  </gmd:distance>
                </gmd:MD_Resolution>
              </gmd:spatialResolution>
            </xsl:otherwise>
          </xsl:choose>
          <gmd:language>
            <gco:CharacterString>eng</gco:CharacterString>
          </gmd:language>
          <gmd:topicCategory>
            <gmd:MD_TopicCategoryCode><xsl:value-of select="$topicCategory"/></gmd:MD_TopicCategoryCode>
          </gmd:topicCategory>
          <gmd:extent>
            <gmd:EX_Extent>
              <gmd:geographicElement>
                <xsl:variable name="xmin">
                  <xsl:copy-of select="str:split(UL,',')[1]"/>
                  <xsl:copy-of select="str:split(LL,',')[1]"/>
                </xsl:variable>
                <xsl:variable name="ymin">
                  <xsl:copy-of select="str:split(LR,',')[2]"/>
                  <xsl:copy-of select="str:split(LL,',')[2]"/>
                </xsl:variable>
                <xsl:variable name="xmax">
                  <xsl:copy-of select="str:split(UR,',')[1]"/>
                  <xsl:copy-of select="str:split(LR,',')[1]"/>
                </xsl:variable>
                <xsl:variable name="ymax">
                  <xsl:copy-of select="str:split(UR,',')[2]"/>
                  <xsl:copy-of select="str:split(UL,',')[2]"/>
                </xsl:variable>
                <gmd:EX_GeographicBoundingBox>
                  <gmd:extentTypeCode>
                    <gco:Boolean>1</gco:Boolean>
                  </gmd:extentTypeCode>
                  <gmd:westBoundLongitude>
                    <gco:Decimal><xsl:value-of select="math:min(exsl:node-set($xmin)/*)"/></gco:Decimal>
                  </gmd:westBoundLongitude>
                  <gmd:eastBoundLongitude>
                    <gco:Decimal><xsl:value-of select="math:max(exsl:node-set($xmax)/*)"/></gco:Decimal>
                  </gmd:eastBoundLongitude>
                  <gmd:southBoundLatitude>
                    <gco:Decimal><xsl:value-of select="math:min(exsl:node-set($ymin)/*)"/></gco:Decimal>
                  </gmd:southBoundLatitude>
                  <gmd:northBoundLatitude>
                    <gco:Decimal><xsl:value-of select="math:max(exsl:node-set($ymax)/*)"/></gco:Decimal>
                  </gmd:northBoundLatitude>
                </gmd:EX_GeographicBoundingBox>
              </gmd:geographicElement>
            </gmd:EX_Extent>
          </gmd:extent>
          <gmd:extent>
            <gmd:EX_Extent>
              <gmd:geographicElement>
                <gmd:EX_BoundingPolygon>
                  <gmd:polygon>
                    <gml:Polygon gml:id="BP01">
                      <gml:exterior> 
                        <gml:LinearRing>
                          <gml:pos><xsl:value-of select="str:replace(LL, ',', ' ')"/></gml:pos>
                          <gml:pos><xsl:value-of select="str:replace(UL, ',', ' ')"/></gml:pos>
                          <gml:pos><xsl:value-of select="str:replace(UR, ',', ' ')"/></gml:pos>
                          <gml:pos><xsl:value-of select="str:replace(LR, ',', ' ')"/></gml:pos>
                          <gml:pos><xsl:value-of select="str:replace(LL, ',', ' ')"/></gml:pos>
                        </gml:LinearRing>
                      </gml:exterior>
                    </gml:Polygon>
                  </gmd:polygon>
                </gmd:EX_BoundingPolygon>
              </gmd:geographicElement>
            </gmd:EX_Extent>
          </gmd:extent>
          <!--
          <gmd:extent>
            <gmd:EX_Extent>
              <gmd:geographicElement>
                <gmd:EX_GeographicDescription>
                  <gmd:geographicIdentifier>
                    <gmd:MD_Identifier>
                      <gmd:authority>
                        <gmd:CI_Citation>
                          <gmd:title>
                            <gco:CharacterString>ANZLIC Geographic Extent Name Register - States and Territories</gco:CharacterString>
                          </gmd:title>
                          <gmd:date>
                            <gmd:CI_Date>
                              <gmd:date>
                                <gco:Date>2003-12-10</gco:Date>
                              </gmd:date>
                              <gmd:dateType>
                                <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode"
                                                       codeListValue="creation"/>
                              </gmd:dateType>
                            </gmd:CI_Date>
                          </gmd:date>
                          <gmd:date>
                            <gmd:CI_Date>
                              <gmd:date>
                                <gco:Date>2011-10-25</gco:Date>
                              </gmd:date>
                              <gmd:dateType>
                                <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode"
                                                     codeListValue="revision"/>
                              </gmd:dateType>
                            </gmd:CI_Date>
                          </gmd:date>
                          <gmd:edition>
                            <gco:CharacterString>1</gco:CharacterString>
                          </gmd:edition>
                          <gmd:identifier>
                            <gmd:MD_Identifier>
                               <gmd:code>
                                  <gco:CharacterString>http://www.ga.gov.au/anzmeta/gen/anzlic-algens.xml#anzlic-state_territory</gco:CharacterString>
                               </gmd:code>
                            </gmd:MD_Identifier>
                          </gmd:identifier>
                          <gmd:citedResponsibleParty xlink:href="www.environment.gov.au"/>
                          <gmd:presentationForm>
                            <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode"
                                                         codeListValue="documentDigital"/>
                          </gmd:presentationForm>
                        </gmd:CI_Citation>
                      </gmd:authority>
                      <gmd:code>
                        <gco:CharacterString>AUSTRALIA</gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmd:geographicIdentifier>
                </gmd:EX_GeographicDescription>
              </gmd:geographicElement>
            </gmd:EX_Extent>
          </gmd:extent>
          -->
          <xsl:for-each select="*[starts-with(name(),'GeographicDescription')]">
            <xsl:if test="normalize-space(.)">
              <gmd:extent>
                <gmd:EX_Extent>
                  <gmd:geographicElement>
                    <gmd:EX_GeographicDescription>
                      <gmd:geographicIdentifier>
                        <gmd:MD_Identifier>
                          <gmd:authority>
                            <gmd:CI_Citation>
                              <gmd:title>
                                <gco:CharacterString>ANZLIC Geographic Extent Name Register</gco:CharacterString>
                              </gmd:title>
                              <gmd:date>
                                <gmd:CI_Date>
                                  <gmd:date>
                                    <gco:Date>2011-10-25</gco:Date>
                                  </gmd:date>
                                  <gmd:dateType>
                                    <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode"
                                                         codeListValue="revision"/>
                                  </gmd:dateType>
                                </gmd:CI_Date>
                              </gmd:date>
                              <gmd:identifier>
                                <gmd:MD_Identifier>
                                   <gmd:code>
                                      <gco:CharacterString>http://www.ga.gov.au/anzmeta/gen/anzlic-algens.xml</gco:CharacterString>
                                   </gmd:code>
                                </gmd:MD_Identifier>
                              </gmd:identifier>
                              <gmd:presentationForm>
                                <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode"
                                                             codeListValue="documentDigital"/>
                              </gmd:presentationForm>
                            </gmd:CI_Citation>
                          </gmd:authority>
                          <gmd:code>
                            <gco:CharacterString><xsl:value-of select="."/></gco:CharacterString>
                          </gmd:code>
                        </gmd:MD_Identifier>
                      </gmd:geographicIdentifier>
                    </gmd:EX_GeographicDescription>
                  </gmd:geographicElement>
                </gmd:EX_Extent>
              </gmd:extent>
            </xsl:if>
          </xsl:for-each>
          <gmd:extent>
            <gmd:EX_Extent>
              <gmd:temporalElement>
                <gmd:EX_TemporalExtent>
                  <gmd:extent>
                    <gml:TimePeriod gml:id="TP01">
                      <gml:beginPosition>
                        <xsl:choose>
                          <xsl:when test="normalize-space(imgdate)">
                            <xsl:choose>
                              <xsl:when test="contains(imgdate, '/')">
                                <xsl:value-of select="str:split(str:split(imgdate, '/')[1], 'T')[1]"/> <!-- Strip off Time, it doesn't validate-->
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:value-of select="str:split(imgdate, 'T')[1]"/><!-- Strip off Time, it doesn't validate-->
                              </xsl:otherwise>
                            </xsl:choose>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:attribute name="indeterminatePosition">unknown</xsl:attribute>
                          </xsl:otherwise>
                        </xsl:choose>
                      </gml:beginPosition>
                      <gml:endPosition>
                        <xsl:choose>
                          <xsl:when test="normalize-space(imgdate)">
                            <xsl:choose>
                              <xsl:when test="contains(imgdate, '/')">
                                <xsl:value-of select="str:split(str:split(imgdate, '/')[2], 'T')[1]"/><!-- Strip off Time, it doesn't validate-->
                              </xsl:when>
                              <xsl:otherwise>
                                <xsl:value-of select="str:split(imgdate, 'T')[1]"/><!-- Strip off Time, it doesn't validate-->
                              </xsl:otherwise>
                            </xsl:choose>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:attribute name="indeterminatePosition">unknown</xsl:attribute>
                          </xsl:otherwise>
                        </xsl:choose>
                      </gml:endPosition>
                    </gml:TimePeriod>
                  </gmd:extent>
                </gmd:EX_TemporalExtent>
              </gmd:temporalElement>
            </gmd:EX_Extent>
         </gmd:extent>
          <gmd:supplementalInformation>
            <gco:CharacterString>
              <xsl:for-each select="*[not(self::quicklook)][not(self::thumbnail)][not(self::abstract)]">
                <xsl:if test="normalize-space(.)">
                  <xsl:value-of select="local-name(.)"/>: <xsl:value-of select="."/>
                  <!--xsl:if test="position() != last()">  |  </xsl:if-->
                  <xsl:if test="position() != last()"><xsl:text>&#xA;</xsl:text></xsl:if><!--insert line break-->
                </xsl:if>
              </xsl:for-each>
            </gco:CharacterString>
          </gmd:supplementalInformation>
        </gmd:MD_DataIdentification>
      </gmd:identificationInfo>
  </xsl:template><!--identificationInfo--> 
  <!--
  -->  
  <xsl:template name="contentInfo">
    <xsl:variable name="tbands" select="str:tokenize(string(bands), ',')"/>
    <xsl:variable name="tnbits" select="str:tokenize(string(nbits), ',')"/>
    <xsl:variable name="tnodata" select="str:tokenize(string(nodata), ',')"/>
    <xsl:variable name="trows" select="str:tokenize(string(rows), ',')"/>
    <xsl:variable name="tcols" select="str:tokenize(string(cols), ',')"/>
    <xsl:variable name="tcellx" select="str:tokenize(string(cellx), ',')"/>
    <xsl:variable name="tcelly" select="str:tokenize(string(celly), ',')"/>
    <xsl:variable name="tdatatype" select="str:tokenize(string(celly), ',')"/>
    <xsl:variable name="tbandcount" select="count($tbands)"/>
    
    <gmd:contentInfo>
      <gmd:MD_ImageDescription>
        <gmd:attributeDescription>
           <gco:RecordType>Image information</gco:RecordType>
        </gmd:attributeDescription>
        <gmd:contentType>
          <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode"
                                          codeListValue="image"/>
        </gmd:contentType>
        <xsl:if test="normalize-space(sunelevation)">
          <gmd:illuminationElevationAngle>
            <gco:Real><xsl:value-of select="normalize-space(sunelevation)"/></gco:Real>
          </gmd:illuminationElevationAngle>
        </xsl:if>
        <xsl:if test="normalize-space(sunazimuth)">
          <gmd:illuminationAzimuthAngle>
            <gco:Real><xsl:value-of select="normalize-space(sunazimuth)"/></gco:Real>
          </gmd:illuminationAzimuthAngle>
        </xsl:if>
        <xsl:if test="normalize-space(cloudcover)">
          <gmd:imagingCondition>
            <gmd:MD_ImagingConditionCode 
                codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ImagingConditionCode"
                codeListValue="cloud"/>
          </gmd:imagingCondition>
          <!--gmd:imageQualityCode>
            <gmd:MD_Identifier>
              <gmd:code gco:nilReason="missing">
                <gco:CharacterString/>
              </gmd:code>
            </gmd:MD_Identifier>
          </gmd:imageQualityCode-->
          <gmd:cloudCoverPercentage>
            <gco:Real><xsl:value-of select="normalize-space(cloudcover)"/></gco:Real>
          </gmd:cloudCoverPercentage>
        </xsl:if>
        <xsl:if test="normalize-space(level)">
          <gmd:processingLevelCode>
            <gmd:MD_Identifier>
              <gmd:code>
                <gco:CharacterString><xsl:value-of select="normalize-space(level)"/></gco:CharacterString>
              </gmd:code>
            </gmd:MD_Identifier>
          </gmd:processingLevelCode>
        </xsl:if>
        <!-- leave these in case we do something with them in the future -->
        <gmd:radiometricCalibrationDataAvailability>
          <gco:Boolean>
            <xsl:choose>
              <xsl:when test="normalize-space(radiometricCalibrationDataAvailability)"><xsl:value-of select="floor(radiometricCalibrationDataAvailability)"/></xsl:when>
              <xsl:otherwise>0</xsl:otherwise>
            </xsl:choose>
          </gco:Boolean>
        </gmd:radiometricCalibrationDataAvailability>
        <gmd:cameraCalibrationInformationAvailability>
          <gco:Boolean>
            <xsl:choose>
              <xsl:when test="normalize-space(cameraCalibrationInformationAvailability)"><xsl:value-of select="floor(cameraCalibrationInformationAvailability)"/></xsl:when>
              <xsl:otherwise>0</xsl:otherwise>
            </xsl:choose>
          </gco:Boolean>
        </gmd:cameraCalibrationInformationAvailability>
        <gmd:filmDistortionInformationAvailability>
          <gco:Boolean>
            <xsl:choose>
              <xsl:when test="normalize-space(filmDistortionInformationAvailability)"><xsl:value-of select="floor(filmDistortionInformationAvailability)"/></xsl:when>
              <xsl:otherwise>0</xsl:otherwise>
            </xsl:choose>
          </gco:Boolean>
        </gmd:filmDistortionInformationAvailability>
        <gmd:lensDistortionInformationAvailability>
          <gco:Boolean>
            <xsl:choose>
              <xsl:when test="normalize-space(lensDistortionInformationAvailability)"><xsl:value-of select="floor(lensDistortionInformationAvailability)"/></xsl:when>
              <xsl:otherwise>0</xsl:otherwise>
            </xsl:choose>
          </gco:Boolean>
        </gmd:lensDistortionInformationAvailability>
      </gmd:MD_ImageDescription>
    </gmd:contentInfo>
    <gmd:contentInfo>
      <gmd:MD_ImageDescription>
        <gmd:attributeDescription>
           <gco:RecordType>Band information</gco:RecordType>
        </gmd:attributeDescription>
        <gmd:contentType>
          <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode"
                                          codeListValue="image"/>
        </gmd:contentType>
        <xsl:call-template name="bands">
          <xsl:with-param name="band" select="1"/>
          <xsl:with-param name="count" select="$tbandcount"/>
          <xsl:with-param name="tbands" select="$tbands"/>
          <xsl:with-param name="tnbits" select="$tnbits"/>
        </xsl:call-template>
      </gmd:MD_ImageDescription>
    </gmd:contentInfo>
  </xsl:template><!--contentInfo-->
  <xsl:template name="bands">
    <xsl:param name="band"  select="'1'"/>
    <xsl:param name="count" select="'1'"/>
    <xsl:param name="tbands"/>
    <xsl:param name="tnbits"/>
    <!--xsl:param name="tnodata"/-->
    <!--xsl:param name="trows"/-->
    <!--xsl:param name="tcols"/-->
    <!--xsl:param name="tcellx"/-->
    <!--xsl:param name="tcelly"/-->
    <!--xsl:param name="tdatatype"/-->
      <xsl:if test="$band &lt;= $count">
        <gmd:dimension>
          <gmd:MD_Band>
            <gmd:descriptor>
              <xsl:choose>
                <xsl:when test="normalize-space($tbands[$band])">
                  <gco:CharacterString><xsl:value-of select="$tbands[$band]"/></gco:CharacterString>
                </xsl:when>
                <xsl:otherwise>
                  <gco:CharacterString><xsl:value-of select="$band"/></gco:CharacterString>
                </xsl:otherwise>
              </xsl:choose>
            </gmd:descriptor>
            <gmd:bitsPerValue>
              <xsl:choose>
                <xsl:when test="normalize-space($tnbits[$band])">
                  <gco:Integer><xsl:value-of select="floor($tnbits[$band])"/></gco:Integer>
                </xsl:when>
                <xsl:otherwise>
                  <gco:Integer><xsl:value-of select="floor($tnbits[1])"/></gco:Integer>
                </xsl:otherwise>
              </xsl:choose>
            </gmd:bitsPerValue>
          </gmd:MD_Band>
        </gmd:dimension>
        <xsl:call-template name="bands">
          <xsl:with-param name="band" select="$band + 1"/>
          <xsl:with-param name="count" select="$count"/>
          <xsl:with-param name="tbands" select="$tbands"/>
          <xsl:with-param name="tnbits" select="$tnbits"/>
        </xsl:call-template>
      </xsl:if>
  </xsl:template><!--bands-->
  <!--
  -->  
  <xsl:template name="distributionInfo">
    <gmd:distributionInfo>
      <gmd:MD_Distribution>
        <gmd:distributionFormat>
          <gmd:MD_Format>
            <gmd:name>
              <gco:CharacterString>
                <xsl:value-of select="normalize-space(filetype)"/>
              </gco:CharacterString>
            </gmd:name>
            <gmd:version>
              <!--gco:CharacterString>none</gco:CharacterString-->
              <gco:CharacterString>Unknown</gco:CharacterString>
            </gmd:version>
          </gmd:MD_Format>
        </gmd:distributionFormat>
        <gmd:distributor>
          <gmd:MD_Distributor>
            <gmd:distributorContact>
              <xsl:call-template name="default_contact">
                <xsl:with-param name="contact" select="'distributor'"/>
              </xsl:call-template>
            </gmd:distributorContact>
            </gmd:MD_Distributor>
        </gmd:distributor>
        <gmd:transferOptions>
            <gmd:MD_DigitalTransferOptions>
                <!--xsl:for-each select="OnlineResource"-->
                <xsl:for-each select="*[starts-with(name(),'OnlineResource')]">
                  <xsl:if test="normalize-space(.)">
                    <xsl:variable name="resource" select="str:toNode(.)"/>
                    <gmd:onLine>
                      <gmd:CI_OnlineResource>
                        <gmd:linkage>
                          <gmd:URL><xsl:value-of select="$resource/URL"/></gmd:URL>
                        </gmd:linkage>
                        <gmd:protocol>
                          <gco:CharacterString><xsl:value-of select="$resource/protocol"/></gco:CharacterString>
                        </gmd:protocol>
                        <xsl:choose>
                          <xsl:when test="normalize-space($resource/name)">
                            <gmd:name>
                              <gco:CharacterString><xsl:value-of select="$resource/name"/></gco:CharacterString>
                            </gmd:name>
                          </xsl:when>
                          <xsl:otherwise>
                            <gmd:name gco:nilReason="missing"><gco:CharacterString/></gmd:name>
                          </xsl:otherwise>
                        </xsl:choose>
                        <xsl:choose>
                          <xsl:when test="normalize-space($resource/description)">
                            <gmd:description><gco:CharacterString><xsl:value-of select="$resource/description"/></gco:CharacterString></gmd:description>
                          </xsl:when>
                          <xsl:otherwise><gmd:description gco:nilReason="missing"><gco:CharacterString/></gmd:description></xsl:otherwise>
                        </xsl:choose>
                        <xsl:if test="normalize-space($resource/function)">
                          <gmd:function>
                            <gmd:CI_OnLineFunctionCode>
                              <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/codeList.xml#CI_OnLineFunctionCode</xsl:attribute>
                              <xsl:attribute name="codeListValue"><xsl:value-of select="normalize-space($resource/function)"/></xsl:attribute>
                            </gmd:CI_OnLineFunctionCode>
                          </gmd:function>
                        </xsl:if>
                      </gmd:CI_OnlineResource>
                    </gmd:onLine>                            
                  </xsl:if>
                </xsl:for-each>
                <xsl:choose>
                  <xsl:when test="normalize-space(mediaid)">
                    <gmd:offLine>
                      <gmd:MD_Medium>
                        <gmd:name>
                          <xsl:choose>
                            <xsl:when test="normalize-space(mediatype)">
                                <gmd:MD_MediumNameCode>
                                  <xsl:attribute name="codeList">http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MediumNameCode</xsl:attribute>
                                  <xsl:attribute name="codeListValue"><xsl:value-of select="normalize-space(mediatype)"/></xsl:attribute>
                                </gmd:MD_MediumNameCode>
                            </xsl:when>
                            <xsl:otherwise>
                                <gmd:MD_MediumNameCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MediumNameCode"
                                                       codeListValue="dvd"/>
                            </xsl:otherwise>
                          </xsl:choose>
                        </gmd:name>
                        <gmd:mediumNote>
                          <gco:CharacterString><xsl:value-of select="normalize-space(mediaid)"/></gco:CharacterString>
                        </gmd:mediumNote>
                      </gmd:MD_Medium>
                    </gmd:offLine>
                  </xsl:when>
                  <xsl:otherwise>
                    <gmd:offLine>
                      <gmd:MD_Medium>
                        <gmd:name>
                            <gmd:MD_MediumNameCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MediumNameCode"
                                                   codeListValue="onLine"/>
                        </gmd:name>
                        <gmd:mediumNote>
                          <gco:CharacterString>File path:<xsl:value-of select="normalize-space(filepath)"/></gco:CharacterString>
                        </gmd:mediumNote>
                      </gmd:MD_Medium>
                    </gmd:offLine>
                  </xsl:otherwise>
                </xsl:choose>
            </gmd:MD_DigitalTransferOptions>
        </gmd:transferOptions>
      </gmd:MD_Distribution>
    </gmd:distributionInfo>
  </xsl:template><!--distributionInfo-->  
  <!--
  -->  
  <xsl:template name="dataQualityInfo">
    <xsl:param name="DQ_Type"/>
    <xsl:param name="DQ_Value"/>
    <xsl:choose>
      <xsl:when test="$DQ_Type='lineage'">
        <gmd:lineage>
          <gmd:LI_Lineage>
            <gmd:statement>
              <gco:CharacterString>
                  <xsl:choose>
                      <xsl:when test="normalize-space(lineage)"><xsl:value-of select="lineage"/></xsl:when>
                      <xsl:otherwise>Please enter dataset LINEAGE</xsl:otherwise>
                  </xsl:choose>
              </gco:CharacterString>
            </gmd:statement>
            <xsl:variable name="tsteps">
              <xsl:element name="demcorrection"><xsl:value-of select="demcorrection"/></xsl:element>
              <xsl:element name="resampling"><xsl:value-of select="resampling"/></xsl:element>
            </xsl:variable>
            <xsl:for-each select="exsl:node-set($tsteps)/*">
              <xsl:if test="normalize-space(.)">
                <gmd:processStep>
                  <gmd:LI_ProcessStep>
                    <gmd:description>
                      <gco:CharacterString><xsl:value-of select="local-name(.)"/>: <xsl:value-of select="normalize-space(.)"/></gco:CharacterString>
                    </gmd:description>
                    <gmd:rationale gco:nilReason="missing"><gco:CharacterString/></gmd:rationale>
                    <gmd:dateTime gco:nilReason="missing"/>
                    <gmd:processor gco:nilReason="missing"></gmd:processor>
                  </gmd:LI_ProcessStep>
                </gmd:processStep>
              </xsl:if>
            </xsl:for-each>
            <gmd:source>
              <gmd:LI_Source>
                <gmd:description>
                  <gco:CharacterString><xsl:choose>
                      <xsl:when test="normalize-space(source)"><xsl:value-of select="source"/></xsl:when>
                      <xsl:otherwise>Please enter dataset SOURCE</xsl:otherwise>
                  </xsl:choose></gco:CharacterString>
                </gmd:description>
              </gmd:LI_Source>
            </gmd:source>
          </gmd:LI_Lineage>
        </gmd:lineage>
      </xsl:when>
      <xsl:otherwise>
        <gmd:report>
          <xsl:element name="gmd:DQ_{$DQ_Type}">
            <gmd:result>
              <gmd:DQ_ConformanceResult>
                <gmd:specification>
                  <gmd:CI_Citation>
                    <!--gmd:title><gco:CharacterString><xsl:value-of select="$DQ_Value"/></gco:CharacterString></gmd:title-->
                    <gmd:title><gco:CharacterString><xsl:value-of select="$DQ_Type"/></gco:CharacterString></gmd:title>
                    <!--xsl:call-template name="UnknownDate"/-->
                    <gmd:date>
                      <gmd:CI_Date>
                        <!--gmd:date gco:nilReason="unknown"></gmd:date-->
                        <gmd:date><gco:Date>
                          <xsl:choose>
                              <xsl:when test="normalize-space(metadatadate)">
                                  <xsl:choose>
                                      <xsl:when test="contains(metadatadate,'T')">
                                        <xsl:value-of select="str:split(metadatadate,'T')[1]"/><!--date doesn't validate with time values-->
                                      </xsl:when>
                                      <xsl:otherwise><xsl:value-of select="metadatadate"/></xsl:otherwise>
                                  </xsl:choose>
                              </xsl:when>
                              <xsl:otherwise><xsl:value-of select="date:format-date(date:date-time(),'yyyy-MM-dd')"/></xsl:otherwise>
                          </xsl:choose>
                        </gco:Date></gmd:date>
                        <gmd:dateType>
                          <gmd:CI_DateTypeCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#CI_DateTypeCode" codeListValue="publication">publication</gmd:CI_DateTypeCode>
                        </gmd:dateType>
                      </gmd:CI_Date>
                    </gmd:date>
                  </gmd:CI_Citation>
                </gmd:specification>
                <xsl:choose>
                  <xsl:when test="normalize-space($DQ_Value)">
                    <gmd:explanation>
                      <gco:CharacterString><xsl:value-of select="$DQ_Value"/></gco:CharacterString>
                    </gmd:explanation>
                  </xsl:when>
                  <xsl:otherwise>
                    <gmd:explanation>
                      <gco:CharacterString>Please enter <xsl:value-of select="$DQ_Type"/> text</gco:CharacterString>
                    </gmd:explanation>
                  </xsl:otherwise>
                </xsl:choose>
                <gmd:pass>
                  <gco:Boolean>1</gco:Boolean>
                </gmd:pass>
                <!--gmd:pass gco:nilReason="missing"> <- This fails validation
                  <gco:Boolean/> 
                </gmd:pass-->
              </gmd:DQ_ConformanceResult>
            </gmd:result>
          </xsl:element><!--xsl:element name="gmd:DQ_{$DQ_Type}"-->
        </gmd:report>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template><!--dataQualityInfo-->
  <!--
  -->  
  <xsl:template name="metadataConstraints">
    <gmd:metadataConstraints>
      <gmd:MD_SecurityConstraints>
        <gmd:useLimitation>
          <gco:CharacterString>Security classification: UNCLASSIFIED</gco:CharacterString>
        </gmd:useLimitation>
        <gmd:classification>
          <gmd:MD_ClassificationCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_ClassificationCode" codeListValue="unclassified">unclassified</gmd:MD_ClassificationCode>
        </gmd:classification>
      </gmd:MD_SecurityConstraints>
    </gmd:metadataConstraints>
    <gmd:metadataConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:useLimitation>
          <gco:CharacterString>Internal access only.</gco:CharacterString>
        </gmd:useLimitation>
        <gmd:accessConstraints>
          <gmd:MD_RestrictionCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_RestrictionCode" codeListValue="restricted">restricted</gmd:MD_RestrictionCode>
        </gmd:accessConstraints>
      </gmd:MD_LegalConstraints>
    </gmd:metadataConstraints>
    <gmd:metadataConstraints>
      <gmd:MD_LegalConstraints>
        <gmd:useLimitation>
          <gco:CharacterString>Internal use only.</gco:CharacterString>
        </gmd:useLimitation>
        <gmd:useConstraints>
          <gmd:MD_RestrictionCode codeList="http://asdd.ga.gov.au/asdd/profileinfo/gmxCodelists.xml#MD_RestrictionCode" codeListValue="restricted">restricted</gmd:MD_RestrictionCode>
        </gmd:useConstraints>
      </gmd:MD_LegalConstraints>
    </gmd:metadataConstraints>
  </xsl:template>
 
  <!--
    S U B R O U T I N E S
  -->
  <xsl:template name="DummyCitation">
    <gmd:CI_Citation>
      <gmd:title gco:nilReason="unknown"><gco:CharacterString/></gmd:title>
      <xsl:call-template name="UnknownDate"/>
    </gmd:CI_Citation>
  </xsl:template><!-- /name="DummyCitation" -->
  <!--
  -->  
  <xsl:template name="UnknownDate">
    <gmd:date>
      <gmd:CI_Date>
        <gmd:date gco:nilReason="unknown"/>
        <gmd:dateType gco:nilReason="unknown"/>
      </gmd:CI_Date>
    </gmd:date>
  </xsl:template><!-- /name="UnknownDate" -->

  <!--
    F U N C T I O N S
  -->
    <func:function name="str:toNode">
        <xsl:param name="strData" />
        <xsl:variable name="arrData" select="str:split(string($strData), '&#10;')"/>
        <xsl:variable name="retData">
            <result>
                <xsl:for-each select="$arrData">
                    <xsl:element name="{str:split(string(.), '|')[1]}"><xsl:value-of select="str:split(string(.), '|')[2]"/></xsl:element>
                </xsl:for-each>
            </result>
        </xsl:variable>
        <func:result select="exsl:node-set($retData)/*" />
    </func:function>
    <func:function name="str:replaceNewLine">
        <xsl:param name="strData" />
        <xsl:variable name="arrData" select="str:split(string($strData), '&#10;')"/>
        <xsl:variable name="retData">
            <xsl:for-each select="$arrData">
                <xsl:value-of select="."/><xsl:if test="position() != last()"><xsl:text>&#xA;</xsl:text></xsl:if><!--insert line break-->
            </xsl:for-each>
        </xsl:variable>
        <func:result select="$retData" />
    </func:function>
    <func:function name="str:striptime">
        <xsl:param name="strDateTime" />
        <xsl:variable name="arrData" select="str:split(string($strData), '&#10;')"/>
        <xsl:variable name="retData">
            <xsl:for-each select="$arrData">
                <xsl:value-of select="."/><xsl:if test="position() != last()"><xsl:text>&#xA;</xsl:text></xsl:if><!--insert line break-->
            </xsl:for-each>
        </xsl:variable>
        <func:result select="$retData" />
    </func:function>

  
</xsl:stylesheet>
