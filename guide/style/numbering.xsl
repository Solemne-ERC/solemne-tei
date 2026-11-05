<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- The guide's numbering, for its HTML and its PDF: the parts by their own numbers, I to X, and their sections under
     them (V.2); divisions without a part's number, such as the specification, have none. -->
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
  exclude-result-prefixes="tei">
  <xsl:template name="numberBodyDiv">
    <xsl:variable name="part" select="ancestor-or-self::tei:div[parent::tei:body]"/>
    <xsl:if test="$part/@n">
      <xsl:value-of select="$part/@n"/>
      <xsl:for-each select="ancestor-or-self::tei:div[ancestor::tei:div[parent::tei:body]]">
        <xsl:text>.</xsl:text>
        <xsl:number count="tei:div"/>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>
