<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- The guide's PDF: TEI's LaTeX stylesheet, run on the guide made into TEI Lite, for LuaLaTeX in Junicode, with the
     preamble in solemne-guide.sty. solemne-tei docs puts the address of TEI's stylesheets in place of
     TEI-STYLESHEETS, and gives the folder of the fonts in fontPath. -->
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
  xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="tei xs">
  <xsl:import href="TEI-STYLESHEETS/latex/latex.xsl"/>
  <xsl:include href="numbering.xsl"/>

  <xsl:param name="fontPath"/>
  <xsl:param name="documentclass">book</xsl:param>
  <xsl:param name="classParameters">10pt,twoside,openany</xsl:param>
  <xsl:param name="latexPaperSize">a4paper</xsl:param>
  <xsl:param name="latexGeometryOptions">twoside,inner=25mm,outer=25mm,top=25mm,bottom=25mm</xsl:param>
  <xsl:param name="typewriterFont">DejaVu Sans Mono</xsl:param>
  <xsl:param name="userpackage">solemne-guide</xsl:param>
  <xsl:param name="hyperSetup">colorlinks=true,linkcolor=solemnelink,urlcolor=solemnelink,bookmarksnumbered=true</xsl:param>

  <!-- TEI's setup takes fontspec's way under XeTeX only. LuaTeX takes it too: ifxetex says yes, and xunicode, which
       only XeTeX needs, counts as loaded. -->
  <xsl:template name="latexSetupHook">
    <xsl:text>
\expandafter\def\csname ver@ifxetex.sty\endcsname{}
\expandafter\def\csname ver@xunicode.sty\endcsname{}
\newif\ifxetex \xetextrue
\def\SolemneFontPath{</xsl:text>
    <xsl:value-of select="$fontPath"/>
    <xsl:text>/}
</xsl:text>
  </xsl:template>

  <!-- The specification, after the parts, has no part's number. -->
  <xsl:template match="tei:body/tei:div[not(@n)]/tei:head">
    <xsl:text>&#10;\chapter*{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}\addcontentsline{toc}{chapter}{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}&#10;</xsl:text>
    <xsl:if test="../@xml:id">
      <xsl:text>\label{</xsl:text>
      <xsl:value-of select="../@xml:id"/>
      <xsl:text>}&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- The title page: the title, the authors, the version and its date, and the imprint; the contents follow. -->
  <xsl:template match="tei:titlePage">
    <xsl:text>&#10;\begin{titlepage}\centering&#10;\vspace*{0.18\textheight}&#10;{\fontsize{28pt}{34pt}\selectfont </xsl:text>
    <xsl:apply-templates select="tei:docTitle/tei:titlePart[1]/node()"/>
    <xsl:text>\par}&#10;</xsl:text>
    <xsl:if test="tei:docTitle/tei:titlePart[2]">
      <xsl:text>\vspace{1.2em}&#10;{\LARGE\itshape </xsl:text>
      <xsl:apply-templates select="tei:docTitle/tei:titlePart[2]/node()"/>
      <xsl:text>\par}&#10;</xsl:text>
    </xsl:if>
    <xsl:text>\vspace{4em}&#10;{\Large </xsl:text>
    <xsl:for-each select="tei:docAuthor">
      <xsl:apply-templates/>
      <xsl:if test="following-sibling::tei:docAuthor">
        <xsl:text>\\[0.4em]&#10;</xsl:text>
      </xsl:if>
    </xsl:for-each>
    <xsl:text>\par}&#10;\vfill&#10;{\large </xsl:text>
    <xsl:apply-templates select="tei:docEdition/node()"/>
    <xsl:text>\\[0.3em]&#10;</xsl:text>
    <xsl:apply-templates select="tei:docDate/node()"/>
    <xsl:text>\par}&#10;\vspace{3em}&#10;\begin{minipage}{0.8\textwidth}\centering\small </xsl:text>
    <xsl:apply-templates select="tei:docImprint/node()"/>
    <xsl:text>\end{minipage}&#10;\end{titlepage}&#10;\tableofcontents&#10;\cleardoublepage&#10;</xsl:text>
  </xsl:template>

  <!-- TEI's reference for each element, class, macro and datatype runs to hundreds of pages: the HTML has it, a page
       for each, and appendix A sums up the elements. The PDF says so once, in place of the reference. -->
  <xsl:template match="tei:div[tei:div[@type = 'refdoc']]">
    <xsl:if test="not(preceding-sibling::tei:div[tei:div[@type = 'refdoc']])">
      <xsl:text>&#10;\par TEI's reference for each element, class, macro and datatype of the schema, with its content
model and attributes, is in the guide's HTML, a page for each; appendix~A lists every element, with its module, its
tier and the attributes the guide defines or changes.\par&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- A table's columns: one whose longest cell is short (names, tiers, checks) is as wide as that cell; the others
       share what is left of the line by their longest cell, counted up to 60 characters. Rows spanning columns
       don't count. -->
  <xsl:template name="makePreamble-complex">
    <xsl:param name="r"/>
    <xsl:variable name="rows" select="tei:row[not(tei:cell/@cols)]"/>
    <xsl:variable name="columns" select="max((1, for $row in $rows return count($row/tei:cell)))"/>
    <xsl:variable name="longest" as="xs:integer*"
      select="for $i in 1 to $columns return max((4, for $c in $rows/tei:cell[$i] return
        string-length(normalize-space($c))))"/>
    <xsl:variable name="short" select="for $l in $longest return $l le 20"/>
    <xsl:variable name="natural" select="for $l in $longest return $l * 0.52 + 0.4"/>
    <xsl:variable name="fixed" select="sum(for $i in 1 to $columns return if ($short[$i]) then $natural[$i] else 0)"/>
    <xsl:variable name="shared" select="sum(for $i in 1 to $columns return if ($short[$i]) then 0 else min((60,
      $longest[$i])))"/>
    <xsl:for-each select="1 to $columns">
      <xsl:variable name="i" select="."/>
      <xsl:text>P{</xsl:text>
      <xsl:choose>
        <xsl:when test="$short[$i]">
          <xsl:value-of select="format-number($natural[$i], '0.00')"/>
          <xsl:text>em</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="share" select="min((60, $longest[$i])) div $shared"/>
          <xsl:text>\dimexpr </xsl:text>
          <xsl:value-of select="format-number($share, '0.000')"/>
          <xsl:text>\linewidth-</xsl:text>
          <xsl:value-of select="format-number($share * $fixed, '0.00')"/>
          <xsl:text>em-</xsl:text>
          <xsl:value-of select="format-number($share * 2 * $columns, '0.00')"/>
          <xsl:text>\tabcolsep\relax</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:text>}</xsl:text>
      <xsl:if test="contains($r, 'rules')">|</xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- A specification group's summary lists the reference's entries, which are in the HTML only. -->
  <xsl:template match="tei:table[@rend = 'specGrpSummary']"/>

  <!-- An element's name links to its reference in the HTML only. -->
  <xsl:template match="tei:ref[starts-with(@target, '#TEI.')]">
    <xsl:apply-templates/>
  </xsl:template>
</xsl:stylesheet>
