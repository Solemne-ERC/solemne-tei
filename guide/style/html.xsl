<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- The guide's HTML: TEI's odd2html, with a page for the title and contents, one for the front matter, one per part
     and one per appendix, the reference split into a page per specification, the parts numbered I to X, and the
     guide's own stylesheet. solemne-tei docs puts the address of TEI's stylesheets in place of TEI-STYLESHEETS. -->
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
  xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.w3.org/1999/xhtml" exclude-result-prefixes="tei xs">
  <xsl:import href="TEI-STYLESHEETS/odds/odd2html.xsl"/>
  <xsl:include href="numbering.xsl"/>

  <!-- A page per division of the front, the body and the back, and one per specification. -->
  <xsl:param name="STDOUT">false</xsl:param>
  <xsl:param name="splitLevel" select="0"/>
  <xsl:param name="splitFrontmatter">true</xsl:param>
  <xsl:param name="splitBackmatter">true</xsl:param>
  <!-- The guide's own stylesheet, and nothing fetched from elsewhere. -->
  <xsl:param name="cssFile">guide.css</xsl:param>
  <xsl:param name="cssPrintFile"/>
  <xsl:param name="cssSecondaryFile"/>
  <!-- The title page says who wrote the guide, once; no page shows the build's fixed date. -->
  <xsl:param name="showTitleAuthor">false</xsl:param>
  <xsl:param name="parentURL"/>
  <xsl:param name="feedbackURL"/>
  <xsl:param name="tocDepth" select="1"/>
  <!-- Pages' titles from the header's title, not from the title page's lines run together. -->
  <xsl:param name="useHeaderFrontMatter">false</xsl:param>

  <!-- Every page but the first: the guide's title, leading to the first page, then the page's own heading. -->
  <xsl:template name="stdheader">
    <xsl:param name="title">(no title)</xsl:param>
    <p class="guide-title">
      <a href="index.html">
        <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[1]"/>
      </a>
    </p>
    <h1 class="maintitle">
      <xsl:copy-of select="$title"/>
    </h1>
  </xsl:template>

  <xsl:function name="tei:generateTitle" as="node()*">
    <xsl:param name="context"/>
    <xsl:value-of select="$context/ancestor-or-self::tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[1]"/>
  </xsl:function>

  <!-- A page of the reference: the guide's title, and the way back to the specification. -->
  <xsl:template name="bodyHook">
    <xsl:if test="self::tei:elementSpec or self::tei:classSpec or self::tei:macroSpec or self::tei:dataSpec">
      <p class="guide-title">
        <a href="index.html">
          <xsl:value-of select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[1]"/>
        </a>
        <xsl:text>, </xsl:text>
        <a href="specification.html">the specification</a>
      </p>
    </xsl:if>
  </xsl:template>

  <xsl:template match="tei:titlePage/tei:docEdition">
    <div class="docEdition">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <!-- Every page's footer: the guide, its version and its licence. -->
  <xsl:template name="stdfooter">
    <xsl:param name="file"/>
    <footer class="guide-footer">
      <xsl:variable name="front" select="/tei:TEI/tei:text/tei:front/tei:titlePage"/>
      <p>
        <a href="index.html">
          <xsl:value-of select="normalize-space(string-join($front/tei:docTitle/tei:titlePart, ': '))"/>
        </a>
        <xsl:text>, </xsl:text>
        <xsl:value-of select="normalize-space($front/tei:docEdition)"/>
        <xsl:text>. Under the Creative Commons Attribution 4.0 licence.</xsl:text>
      </p>
    </footer>
  </xsl:template>
</xsl:stylesheet>
