<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: MIT -->
<!-- Generated from solemne.odd 0.3.0 (SHA-256 3a5f76c87dbd2051b15033b07ce726640b7f7b25893e2ed3cf7f7122c1a3a4f3) by solemne-tei build. Edit the ODD, not this file. -->
<!--
This schema is made from TEI P5 4.12.0 by the TEI Consortium (https://tei-c.org/), which distributes it under the Creative Commons Attribution 3.0 Unported licence (https://creativecommons.org/licenses/by/3.0/) and under the BSD 2-Clause licence:

Copyright 2026 TEI Consortium.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and
  the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions
  and the following disclaimer in the documentation and/or other materials provided with the
  distribution.

This software is provided by the copyright holders and contributors "as is" and any express or
implied warranties, including, but not limited to, the implied warranties of merchantability and
fitness for a particular purpose are disclaimed. In no event shall the copyright holder or
contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential
damages (including, but not limited to, procurement of substitute goods or services; loss of use,
data, or profits; or business interruption) however caused and on any theory of liability, whether
in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of
the use of this software, even if advised of the possibility of such damage.
-->
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
   <title>ISO Schematron rules</title>
   <!-- This file generated 1970-01-01 by 'extract-isosch.xsl'. -->
   <!-- ********************* -->
   <!-- namespaces, declared: -->
   <!-- ********************* -->
   <ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>
   <ns prefix="xs" uri="http://www.w3.org/2001/XMLSchema"/>
   <ns prefix="rng" uri="http://relaxng.org/ns/structure/1.0"/>
   <ns prefix="rna" uri="http://relaxng.org/ns/compatibility/annotations/1.0"/>
   <ns prefix="sch" uri="http://purl.oclc.org/dsdl/schematron"/>
   <ns prefix="sch1x" uri="http://www.ascc.net/xml/schematron"/>
   <!-- ******************************************************** -->
   <!-- constraints in en, und, mul, zxx, of which there are 115 -->
   <!-- ******************************************************** -->
   <pattern id="schematron-constraint-CMC_generatedBy_within_post-1">
      <rule context="tei:*[@generatedBy]">
         <assert test="ancestor-or-self::tei:post">The @generatedBy attribute is for use within a &lt;post&gt; element.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-att-datable-w3c-when-2">
      <rule context="tei:*[@when]">
         <report test="@notBefore|@notAfter|@from|@to" role="nonfatal">The @when attribute cannot be used with any other att.datable.w3c attributes.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-att-datable-w3c-from-3">
      <rule context="tei:*[@from]">
         <report test="@notBefore" role="nonfatal">The @from and @notBefore attributes cannot be used together.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-att-datable-w3c-to-4">
      <rule context="tei:*[@to]">
         <report test="@notAfter" role="nonfatal">The @to and @notAfter attributes cannot be used together.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-only_1_ODD_source-5">
      <rule context="tei:*[@source]">
         <let name="srcs" value="tokenize( normalize-space(@source),' ')"/>
         <report test="(   self::tei:classRef                                 | self::tei:dataRef                                 | self::tei:elementRef                                 | self::tei:macroRef                                 | self::tei:moduleRef                                 | self::tei:schemaSpec )                                   and                                   $srcs[2]"> When used on a schema description element (like &lt;<value-of select="name(.)"/>&gt;), the @source attribute should have only 1 value. (This one has <value-of select="count($srcs)"/>.)</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-targetLang-6">
      <rule context="tei:*[not(self::tei:schemaSpec)][@targetLang]">
         <assert test="@target">@targetLang should only be used on &lt;<name/>&gt; if @target is specified.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-spanTo-points-to-following-7">
      <rule context="tei:*[ starts-with( @spanTo, '#') ]">
         <assert test="id( substring( @spanTo, 2 ) ) &gt;&gt; ."> The element indicated by @spanTo (<value-of select="@spanTo"/>) must follow the current &lt;<name/>&gt; element.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-subtypeTyped-8">
      <rule context="tei:*[@subtype]">
         <assert test="@type"> The &lt;<name/>&gt; element should not be categorized in detail with @subtype unless also categorized in general with @type.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-calendar_attr_on_empty_element-9">
      <rule context="tei:*[@calendar]">
         <assert test="string-length( normalize-space(.) ) gt 0"> @calendar indicates one or more systems or calendars to which the date represented by the content of this element belongs, but this &lt;<name/>&gt; element has no textual content.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-p-in-ab-or-p-10">
      <rule context="tei:p">
         <report test="(ancestor::tei:ab or ancestor::tei:p) and                        not( ancestor::tei:floatingText                           | parent::tei:exemplum                           | parent::tei:item                           | parent::tei:note                           | parent::tei:q                           | parent::tei:quote                           | parent::tei:remarks                           | parent::tei:said                           | parent::tei:sp                           | parent::tei:stage                           | parent::tei:cell                           | parent::tei:figure )"> Abstract model violation: Paragraphs may not occur inside other paragraphs or &lt;ab&gt; elements.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-p-in-l-11">
      <rule context="tei:l//tei:p">
         <assert test="ancestor::tei:floatingText | parent::tei:figure | parent::tei:note"> Abstract model violation: Metrical lines (&lt;l&gt; elements) may not contain higher-level structural elements such as &lt;div&gt;, &lt;p&gt;, or &lt;ab&gt;, unless &lt;p&gt; is a child of &lt;figure&gt; or &lt;note&gt;, or is a descendant of &lt;floatingText&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-fragment-next-12">
      <rule context="tei:*[@next]">
         <let name="next"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@next), '#')]"/>
         <assert id="fragment-next"
                 test="count($next) = 1 and local-name($next) = local-name() and                 normalize-space($next/@prev) = concat('#', @xml:id)">&lt;<name/>&gt;'s @next (<value-of select="@next"/>) points to the next fragment in the file, a &lt;<name/>&gt; whose @prev points back.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-fragment-prev-13">
      <rule context="tei:*[@prev]">
         <let name="prev"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@prev), '#')]"/>
         <assert id="fragment-prev"
                 test="count($prev) = 1 and local-name($prev) = local-name() and                 normalize-space($prev/@next) = concat('#', @xml:id)">&lt;<name/>&gt;'s @prev (<value-of select="@prev"/>) points to the previous fragment in the file, a &lt;<name/>&gt; whose @next points back.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-fragment-attributes-14">
      <rule context="tei:*[@prev]">
         <let name="prev"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@prev), '#')]"/>
         <let name="other" value="@*[not(name() = ('xml:id', 'prev', 'next'))]"/>
         <assert id="fragment-attributes"
                 test="every $a in $other satisfies (self::tei:seg and name($a) =                 'type' and $a = $prev/@type)">&lt;<name/>&gt; is a later fragment (it has @prev): it carries only its xml:id, @prev and @next, and the span's other attributes (<value-of select="string-join(for $a                 in $other return concat('@', name($a)), ', ')"/>) go on its first fragment.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-fragment-order-15">
      <rule context="tei:*[@next]">
         <let name="next"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@next), '#')]"/>
         <assert id="fragment-order" test="every $n in $next satisfies $n &gt;&gt; .">&lt;<name/>&gt;'s @next (<value-of select="@next"/>) points to a fragment later in the file: the fragments follow the text's order.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-deprecationInfo-only-in-deprecated-16">
      <rule context="tei:desc[ @type eq 'deprecationInfo']">
         <assert test="../@validUntil">Information about a deprecation should only be present in a specification element that is being deprecated: that is, only an element that has a @validUntil attribute should have a child &lt;desc type="deprecationInfo"&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-gap-quantity-unit-17">
      <rule context="tei:gap[@quantity or @unit]">
         <assert id="gap-quantity-unit" test="@quantity and @unit">A gap's quantity is given with its unit (leaves, lines, words or chars), and a unit with its quantity.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-span-bounds-18">
      <rule context="tei:*[@notBefore or @notAfter][not(self::tei:locus or self::tei:biblScope or               self::tei:citedRange)]">
         <assert id="date-span-bounds"
                 role="warning"
                 test="@notBefore and @notAfter">A point between bounds gives both, @notBefore and @notAfter.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-from-to-19">
      <rule context="tei:*[@from or @to][not(self::tei:locus or self::tei:biblScope or               self::tei:citedRange)]">
         <assert id="date-from-to" role="warning" test="@from and @to">A span gives both its ends, @from and @to.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-bounds-order-20">
      <rule context="tei:*[(@notBefore and @notAfter) or (@from and @to)][not(self::tei:locus or               self::tei:biblScope or self::tei:citedRange)]">
         <let name="first"
              value="for $b in (@notBefore, @from) return concat($b, substring('-01-01',                 string-length($b) - 3))"/>
         <let name="last"
              value="for $b in (@notAfter, @to) return concat($b, substring('-12-31',                 string-length($b) - 3))"/>
         <assert id="date-bounds-order"
                 test="(not(@notBefore and @notAfter) or $first[1] le $last[1]) and                 (not(@from and @to) or $first[last()] le $last[last()])">No bound comes after its pair: @notBefore before @notAfter, @from before @to.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-edtf-form-21">
      <rule context="tei:*[@when-custom or @from-custom or @to-custom]">
         <let name="day"
              value="'-?[0-9]{2}([0-9]{2}|[0-9]X|XX)(-([0-9]{2}|XX)(-([0-9]{2}|XX))?)?[~?%]?'"/>
         <let name="item" value="concat('(', $day, ')(\.\.(', $day, '))?')"/>
         <let name="edtf"
              value="concat('^((', $day, ')|\[(', $item, ')(,(', $item, '))*\])$')"/>
         <assert id="date-edtf-form"
                 test="@datingMethod = '#edtf' and (every $v in (@when-custom,                 @from-custom, @to-custom) satisfies matches(normalize-space($v), $edtf))">An EDTF value is a date (0813, 0816-08, 0813-06-13), its last digits unspecified (08XX) or itself marked circa or uncertain (~, ?, %), or a set of them ([0755,0756], [0867..0900]); and the element points to EDTF by @datingMethod="#edtf".</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-edtf-bounds-22">
      <rule context="tei:*[@datingMethod = '#edtf'][@when-custom or @from-custom or @to-custom]">
         <let name="w" value="normalize-space(@when-custom)"/>
         <let name="wy"
              value="tokenize(replace($w, '[^0-9X]+', ' '), ' ')[string-length(.) = 4]"/>
         <let name="wlo"
              value="min(for $y in $wy return xs:integer(translate($y, 'X', '0')))"/>
         <let name="whi"
              value="max(for $y in $wy return xs:integer(translate($y, 'X', '9')))"/>
         <let name="lo"
              value="for $b in (@notBefore, @when)[1] return substring($b, 1, 4)"/>
         <let name="hi"
              value="for $b in (@notAfter, @when)[1] return substring($b, 1, 4)"/>
         <let name="blo"
              value="if ($lo castable as xs:integer) then xs:integer($lo) else ()"/>
         <let name="bhi"
              value="if ($hi castable as xs:integer) then xs:integer($hi) else ()"/>
         <let name="point"
              value="empty($wlo) or empty($blo) or empty($bhi) or (if (matches($w, '[~?%]'))                 then $blo le $wlo and $whi le $bhi else if (contains($w, 'X')) then abs($blo - $wlo) le 1 and                 abs($bhi - $whi) le 1 else $blo eq $wlo and $bhi eq $whi)"/>
         <let name="f" value="normalize-space(@from-custom)"/>
         <let name="flo"
              value="min(for $y in tokenize(replace($f, '[^0-9X]+', ' '), ' ')[string-length(.) =                 4] return xs:integer(translate($y, 'X', '0')))"/>
         <let name="fb" value="substring(@from, 1, 4)"/>
         <let name="bf"
              value="if ($fb castable as xs:integer) then xs:integer($fb) else ()"/>
         <let name="start"
              value="empty($flo) or empty($bf) or (if (matches($f, '[~?%]')) then $bf le $flo                 else if (contains($f, 'X')) then abs($bf - $flo) le 1 else $bf eq $flo)"/>
         <let name="t" value="normalize-space(@to-custom)"/>
         <let name="thi"
              value="max(for $y in tokenize(replace($t, '[^0-9X]+', ' '), ' ')[string-length(.) =                 4] return xs:integer(translate($y, 'X', '9')))"/>
         <let name="tb" value="substring(@to, 1, 4)"/>
         <let name="bt"
              value="if ($tb castable as xs:integer) then xs:integer($tb) else ()"/>
         <let name="end"
              value="empty($thi) or empty($bt) or (if (matches($t, '[~?%]')) then $thi le $bt                 else if (contains($t, 'X')) then abs($bt - $thi) le 1 else $bt eq $thi)"/>
         <assert id="date-edtf-bounds"
                 role="warning"
                 test="$point and $start and $end">The bounds agree with the EDTF, by years: an exact date has the bounds' years, a century or decade (08XX) differs by a year at most, a circa or uncertain date lies within them.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-version-choices-23">
      <rule context="tei:bibl[tei:ptr[@type = ('canonical', 'stand-in')]]">
         <assert id="version-choices"
                 test="count(tei:ptr[@type = 'canonical']) le 1 and count(tei:ptr[@type                 = 'stand-in']) le 1">A work names at most one canonical version (ptr type="canonical") and one version that stands in for it (ptr type="stand-in").</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-ptrAtts-24">
      <rule context="tei:ptr">
         <report test="@target and @cRef">Only one of the attributes @target and @cRef may be supplied on &lt;<name/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-refAtts-25">
      <rule context="tei:ref">
         <report test="@target and @cRef">Only one of the attributes @target and @cRef may be supplied on &lt;<name/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-links-list-26">
      <rule context="tei:standOff//tei:note[@type = 'links']">
         <assert id="links-list"
                 test="tei:list[@type = 'links'] and not(text()[normalize-space()])">A note of links holds a list of links, and no words of its own.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-link-target-27">
      <rule context="tei:standOff//tei:list[@type = 'links']/tei:item">
         <assert id="link-target" test="tei:ref[@target][normalize-space(.) != '']">A link has a @target and words.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-link-authority-28">
      <rule context="tei:note[@type = 'links']//tei:ref[@target]">
         <let name="authorities"
              value="'(mirabileweb\.it/(author|title|manuscript)/|wikidata\.org/(wiki|entity)/Q|viaf\.org/viaf/|d-nb\.info/gnd/|geonames\.org/[0-9]|vocab\.getty\.edu/(page/)?tgn/|pleiades\.stoa\.org/places/|sdbm\.library\.upenn\.edu/|manus\.iccu\.sbn\.it/|medieval\.bodleian\.ox\.ac\.uk/catalog/)'"/>
         <assert id="link-authority"
                 role="warning"
                 test="not(matches(@target, $authorities))">An authority's record is an id: an idno typed by the authority, not a link in a note of links (<value-of select="@target"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-gloss-list-must-have-labels-29">
      <rule context="tei:list[@type='gloss']">
         <assert test="tei:label"> The content of a "gloss" list should include a sequence of one or more pairs of a &lt;label&gt; element followed by an &lt;item&gt; element.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-text-note-type-30">
      <rule context="tei:body//tei:note">
         <assert id="text-note-type" test="@type = ('source', 'parallel', 'editorial')">A note in the text is typed source, parallel or editorial.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-note-has-content-31">
      <rule context="tei:note">
         <assert id="note-has-content" test="normalize-space(.) != '' or @source or *">A note holds words, or its codes in @source.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-source-note-codes-32">
      <rule context="tei:body//tei:note[@type = 'source']">
         <report id="source-note-codes"
                 role="warning"
                 test="some $w in tokenize(normalize-space(.),                 '[\s;,]+') satisfies matches($w,                 '^(cf_)?((C|D|COLL|P|EP|H|EX|W)\.[A-Za-z0-9.\-]+(_[A-Za-z0-9.\-]+)?|[1-4]?[A-Z]{2,4}_[0-9]+(_[0-9]+)?(-[0-9]+)?)$')">A source note's words hold a code (<value-of select="normalize-space(.)"/>): it belongs in @source.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-record-pointer-in-ref-33">
      <rule context="tei:*[@key or @corresp]">
         <report id="record-pointer-in-ref"
                 role="warning"
                 test="some $p in                 tokenize(normalize-space(string-join((@key, @corresp), ' ')), ' ') satisfies matches($p,                 '^#?[Nn]ew_[A-Za-z]+_|^#?(PERS\.\d+|solemne_person_\d+)$|^https?://\S+/id/(person|place|institution|event|manuscript|publication)/')">&lt;<name/>&gt; points to a record in @key or @corresp (<value-of select="normalize-space(string-join((@key,                 @corresp), ' '))"/>): a record is pointed to by @ref, on a name inside provenance, acquisition and origin.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-first-formal-34">
      <rule context="tei:fileDesc/tei:titleStmt">
         <assert id="title-first-formal" test="tei:title[1][@type = 'formal']">The title statement opens with a title typed formal.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-one-formal-35">
      <rule context="tei:fileDesc/tei:titleStmt">
         <assert id="title-one-formal" test="count(tei:title[@type = 'formal']) = 1">The title statement has one formal title.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-type-36">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title">
         <assert id="title-type" test="@type = ('formal', 'alias', 'other')">A title in the title statement is typed formal, alias or other.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-alias-words-37">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title">
         <assert id="title-alias-words"
                 test="not(@type = 'alias') or normalize-space(.) != ''">An alias isn't empty.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-other-source-38">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title">
         <assert id="title-other-source"
                 role="warning"
                 test="not(@type = 'other') or @source">A title typed other names its source in @source.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-idnos-39">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']">
         <assert id="formal-title-idnos"
                 test="count(tei:idno[not(@type)]) = 1 and count(tei:idno[@type =                   'category']) = 1 and count(tei:idno[@type = 'type']) = 1 and (every $level in ('work', 'version',                   'witness', 'transcription') satisfies count(tei:idno[@type = $level]) le 1)">The formal title holds the document's code (an identifier without a type), its category and its type, once each, and at most one permalink for each level the file belongs to.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-idno-in-formal-title-40">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title/tei:idno">
         <assert id="idno-in-formal-title" test="parent::tei:title[@type = 'formal']">An identifier in the title statement stands in the formal title.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-idno-type-41">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title/tei:idno">
         <assert id="idno-type"
                 test="not(@type) or @type = ('category', 'type', 'work', 'version',                   'witness', 'transcription')">An identifier in the formal title is the code (without a type), the category, the type, or the permalink of a level (work, version, witness, transcription).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-code-format-42">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[not(@type)]">
         <assert id="code-format"
                 test="matches(normalize-space(.),                   '^[A-Z]+\.[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z][A-Za-z0-9]*(-[A-Za-z0-9]+)*)*$')">The document's code (<value-of select="normalize-space(.)"/>) begins with its category's prefix and a dot, holds only letters, digits, dots and hyphens, and joins its title's parts, the date among them, by hyphens; a part after another dot is a source part, beginning with a letter.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-code-category-43">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[not(@type)]">
         <let name="category"
              value="normalize-space(../tei:idno[@type = 'category'][1])"/>
         <let name="prefix" value="substring-before(normalize-space(.), '.')"/>
         <assert id="code-category"
                 test="$category = ('', 'UNK') or $prefix = (if                   ($category = ('SYSCOLL', 'CHRCOLL')) then 'COLL' else $category)">The document's code (<value-of select="normalize-space(.)"/>) begins with its category's prefix (<value-of select="if ($category = ('SYSCOLL', 'CHRCOLL')) then 'COLL' else $category"/>, for the category <value-of select="$category"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-code-manuscript-44">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[not(@type)]">
         <assert id="code-manuscript"
                 test="not(contains(normalize-space(.), '.ms-')) or                   ancestor::tei:fileDesc/tei:sourceDesc//tei:msDesc">A manuscript's code (<value-of select="normalize-space(.)"/>) goes with the manuscript's description (msDesc) in the sourceDesc.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-code-matches-file-name-45">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[not(@type)]">
         <assert id="code-matches-file-name"
                 role="warning"
                 test="not(matches(base-uri(.),                   '/[A-Z]+\.[^/]*\.xml$')) or ends-with(base-uri(.), concat('/',                   encode-for-uri(normalize-space(.)), '.xml'))">A file named by a code is named by its document's code (<value-of select="normalize-space(.)"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-category-value-46">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[@type = 'category']">
         <assert id="category-value"
                 test="normalize-space(.) = ('SYSCOLL', 'CHRCOLL', 'C', 'D', 'P', 'H',                   'EX', 'EP', 'LR', 'CPT', 'CHA', 'UNK')">The document's category (<value-of select="normalize-space(.)"/>) is one of SYSCOLL, CHRCOLL, C, D, P, H, EX, EP, LR, CPT, CHA, UNK.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-document-type-value-47">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[@type = 'type']">
         <assert id="document-type-value"
                 test="normalize-space(.) = ('edition', 'manuscript',                   'reconstruction', 'hypothesis', 'placeholder')">The document's type (<value-of select="normalize-space(.)"/>) is one of edition, manuscript, reconstruction, hypothesis, placeholder.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-type-manuscript-48">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[@type = 'type']">
         <assert id="type-manuscript"
                 test="not(normalize-space(.) = 'manuscript') or                   ancestor::tei:fileDesc/tei:sourceDesc//tei:msDesc">A document typed manuscript has the manuscript's description (msDesc) in its sourceDesc.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-decls-target-49">
      <rule context="tei:*[@decls]">
         <assert id="decls-target"
                 test="every $t in tokenize(normalize-space(@decls), ' ') satisfies                   (starts-with($t, '#') and exists(/tei:TEI/tei:teiHeader//(tei:correction |                   tei:segmentation)[@xml:id = substring($t, 2)]))">@decls (<value-of select="normalize-space(@decls)"/>) points to a correction or a segmentation in the header.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-correction-default-50">
      <rule context="tei:editorialDecl[count(tei:correction) gt 1]">
         <assert id="correction-default"
                 test="count(tei:correction[@default = 'true']) = 1">Of several corrections, one is the default (@default="true"): the whole text's.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-inferred-units-pointed-to-51">
      <rule context="tei:segmentation[@type = 'inferred-units'][@default = 'false']">
         <let name="id" value="concat('#', @xml:id)"/>
         <assert id="inferred-units-pointed-to"
                 role="warning"
                 test="@xml:id and                   //@decls[tokenize(normalize-space(.), ' ') = $id]">A statement of inferred units for some divisions (@default="false") is pointed to by their @decls.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-quotationContents-52">
      <rule context="tei:quotation">
         <report test="not( @marks )  and  not( tei:p )"> On &lt;<name/>&gt;, either the @marks attribute should be used, or a paragraph of description provided.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-citestructure-outer-match-53">
      <rule context="tei:citeStructure[not(parent::tei:citeStructure)]">
         <assert test="starts-with(@match,'/')">An XPath in @match on the outer &lt;<name/>&gt; must start with '/'.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-citestructure-inner-match-54">
      <rule context="tei:citeStructure[parent::tei:citeStructure]">
         <assert test="not(starts-with(@match,'/'))">An XPath in @match must not start with '/' except on the outer &lt;<name/>&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-same-as-prefix-declared-55">
      <rule context="tei:*[@sameAs]">
         <let name="declared" value="/tei:TEI/tei:teiHeader//tei:prefixDef/@ident"/>
         <assert id="same-as-prefix-declared"
                 test="every $id in tokenize(normalize-space(@sameAs), ' ')                   satisfies (not(matches($id, '^[A-Za-z][A-Za-z0-9+.\-]*:')) or matches($id, '^https?:') or                   substring-before($id, ':') = $declared)">The prefixes in @sameAs (<value-of select="normalize-space(@sameAs)"/>) are declared in the header, by prefixDef in listPrefixDef.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-prefix-known-56">
      <rule context="tei:prefixDef">
         <assert id="prefix-known"
                 role="warning"
                 test="@ident = ('scta', 'clavis', 'pseudoisidor',                   'corpuscorporum')">The prefix <value-of select="@ident"/> isn't one the application knows (scta, clavis, pseudoisidor, corpuscorporum).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-script-term-57">
      <rule context="tei:handNote[@script]">
         <let name="terms"
              value="('capitalsSquare', 'capitalsRustic', 'uncial', 'halfUncial',                 'minusculeInsular', 'minusculeVernacular', 'minusculeCaroline', 'minuscule', 'protogothic',                 'textualisNorthern', 'textualisSouthern', 'semitextualis', 'cursivaAntiquior', 'cursiva', 'hybrida',                 'gothicoAntiqua', 'humanistica', 'humanisticaTextualis', 'humanisticaSemitextualis',                 'humanisticaCursiva', 'muhaqqaq', 'rayhani', 'naskh', 'maghribi', 'bihari', 'nasta_liq', 'thuluth',                 'tawqi_', 'riqa_', 'ghubar', 'ta_liq', 'diwani', 'ruq_ah', 'siyaqah', 'unknown')"/>
         <assert id="script-term"
                 role="warning"
                 test="every $s in tokenize(normalize-space(@script), ' ')                 satisfies $s = $terms">The script <value-of select="@script"/> isn't among the vocabulary's seeds: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-execution-term-58">
      <rule context="tei:handNote[@execution]">
         <let name="terms" value="('formata', 'libraria', 'currens')"/>
         <assert id="execution-term" role="warning" test="@execution = $terms">The execution <value-of select="@execution"/> isn't among the vocabulary's seeds: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-hand-declared-59">
      <rule context="tei:*[@hand]">
         <assert id="hand-declared"
                 test="every $h in tokenize(normalize-space(@hand), ' ')[starts-with(.,                 '#')] satisfies //tei:handNote[@xml:id = substring($h, 2)]">@hand points to a hand the file describes, a handNote with that xml:id (<value-of select="@hand"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-date-calendar-60">
      <rule context="tei:origDate[not(@type = 'undated')] | tei:text//tei:date">
         <assert id="date-calendar" test="@calendar">A manuscript's date and a date in the text name the calendar of their words by @calendar: #gregorian for a modern statement ("sec. IX"), the source's own otherwise (a Julian day, an era).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-calendar-declared-61">
      <rule context="tei:*[@calendar or @datingMethod]">
         <assert id="calendar-declared"
                 test="every $p in tokenize(normalize-space(string-join((@calendar,                 @datingMethod), ' ')), ' ') satisfies (starts-with($p, '#') and                 //tei:calendarDesc/tei:calendar[@xml:id = substring($p, 2)])">@calendar and @datingMethod point to a calendar declared in the profile description's calendarDesc (<value-of select="string-join((@calendar, @datingMethod), ' ')"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-text-elements-62">
      <rule context="tei:body//tei:*">
         <assert id="text-elements"
                 test="local-name() = ('div', 'head', 'p', 'note', 'pb', 'lb', 'gap',                 'persName', 'placeName', 'eventName', 'bibl', 'cit', 'quote', 'ref', 'seg', 'date', 'subst', 'add',                 'del', 'unclear', 'foreign', 'choice', 'corr', 'sic', 'abbr', 'expan', 'supplied', 'rs',                 'anchor')">&lt;<name/>&gt; isn't one of the text's elements.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-unit-alone-63">
      <rule context="tei:div[@type = 'unit']">
         <assert id="unit-alone" test="count(../tei:div) gt 1">A unit stands alone in its division: its paragraphs belong to the division itself.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-unit-holds-text-64">
      <rule context="tei:div[@type = 'unit']">
         <assert id="unit-holds-text" test="not(tei:div) and not(tei:head)">A unit holds paragraphs only, without headings or divisions.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-register-item-in-register-65">
      <rule context="tei:div[@type = 'registerItem']">
         <assert id="register-item-in-register"
                 test="parent::tei:div[@type = 'register']">A register item stands in a register.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-number-heading-n-66">
      <rule context="tei:div[tei:head[@type = 'number']]">
         <assert id="number-heading-n" test="@n">A division with a number heading (<value-of select="normalize-space(tei:head[@type = 'number'][1])"/>) has @n.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-div-in-l-67">
      <rule context="tei:l//tei:div">
         <assert test="ancestor::tei:floatingText"> Abstract model violation: Metrical lines (&lt;l&gt; elements) may not contain higher-level structural elements such as &lt;div&gt;, unless &lt;div&gt; is a descendant of &lt;floatingText&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-div-in-ab-or-p-68">
      <rule context="tei:div">
         <report test="(ancestor::tei:p or ancestor::tei:ab) and not(ancestor::tei:floatingText)"> Abstract model violation: &lt;p&gt; and &lt;ab&gt; may not contain higher-level structural elements such as &lt;div&gt;, unless &lt;div&gt; is a descendant of &lt;floatingText&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-event-described-69">
      <rule context="tei:event">
         <assert id="event-described" test="@ref or tei:eventName or tei:p">An event points to a record (@ref) or describes one, with eventName or p.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-event-words-70">
      <rule context="tei:event/tei:desc | tei:event/tei:p">
         <assert id="event-words" test="normalize-space(.) != ''">An event's description isn't empty.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-floruit-dates-71">
      <rule context="tei:floruit">
         <assert id="floruit-dates"
                 test="@when or @notBefore or @notAfter or @from or @to or @period">A floruit gives its dates in its attributes.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-relation-term-72">
      <rule context="tei:relation[@name]">
         <let name="terms"
              value="('isTextOf', 'derivedFrom', 'versionOf', 'witnessOf', 'transcriptionOf',                 'in', 'isVerbatimOf', 'isVariantOf', 'isShorterVersionOf', 'translationOf', 'revisionOf',                 'abridgementOf', 'augmentationOf', 'adaptationOf', 'basedOn', 'origin', 'ownedBy', 'scribe',                 'artist', 'author', 'enactedAt', 'tookPlaceAt', 'holdsOfficeIn', 'lists', 'sameScribeAs',                 'sameHandAs')"/>
         <assert id="relation-term" role="warning" test="@name = $terms">The relation type <value-of select="@name"/> isn't among the guide's types: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-person-id-73">
      <rule context="tei:standOff//tei:listPerson/tei:person">
         <assert id="person-id"
                 test="matches(@xml:id, '^(PERS\.\d+|solemne_person_\d+|new_person_\S+)$')">A person in the standOff has an @xml:id: a record's (PERS. and a number, or solemne_person_ and a number), or a placeholder's (new_person_ and a name).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-person-main-name-74">
      <rule context="tei:standOff//tei:listPerson/tei:person">
         <assert id="person-main-name"
                 test="count(tei:persName[@type = 'main']) = 1 or                 not(starts-with(@xml:id, 'new_person_'))">A new person has one main name (persName typed main).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-ref-or-key-or-name-75">
      <rule context="tei:relation">
         <assert test="@ref or @key or @name">One of the attributes @name, @ref or @key must be supplied.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-active-mutual-76">
      <rule context="tei:relation">
         <report test="@active and @mutual">Only one of the attributes @active and @mutual may be supplied.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-active-passive-77">
      <rule context="tei:relation">
         <report test="@passive and not(@active)">the attribute @passive may be supplied only if the attribute @active is supplied.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-manuscript-unit-78">
      <rule context="tei:msDesc">
         <assert id="manuscript-unit" test="tei:msPart">A manuscript's description has at least one codicological unit (msPart), with its own identifier: the unit holds the physical description, the date, the hands and the decoration.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-description-elements-79">
      <rule context="tei:msDesc//*[not(ancestor::*[self::tei:bibl or self::tei:biblStruct or self::tei:listBibl               or self::tei:persName or self::tei:placeName or self::tei:orgName][ancestor::tei:msDesc])]">
         <let name="profile"
              value="('msIdentifier', 'country', 'region', 'settlement', 'institution',                 'repository', 'collection', 'idno', 'altIdentifier', 'msName', 'msPart', 'msContents', 'summary',                 'textLang', 'msItem', 'locus', 'locusGrp', 'author', 'title', 'rubric', 'incipit', 'explicit',                 'finalRubric', 'colophon', 'note', 'bibl', 'biblStruct', 'listBibl', 'physDesc', 'p', 'objectDesc',                 'supportDesc', 'support', 'extent', 'dimensions', 'height', 'width', 'depth', 'foliation',                 'collation', 'condition', 'layoutDesc', 'layout', 'handDesc', 'handNote', 'decoDesc', 'decoNote',                 'additions', 'bindingDesc', 'binding', 'term', 'history', 'origin', 'origDate', 'origPlace',                 'provenance', 'acquisition', 'additional', 'adminInfo', 'recordHist', 'source', 'surrogates',                 'persName', 'placeName', 'orgName', 'date', 'foreign', 'hi', 'ref')"/>
         <let name="placed"
              value="(not(self::tei:msContents) or parent::tei:msPart) and                 (not(parent::tei:physDesc/parent::tei:msDesc) or self::tei:bindingDesc) and (not(self::tei:bindingDesc)                 or ../parent::tei:msDesc) and (not(self::tei:msPart) or parent::tei:msDesc) and                 (not(parent::tei:adminInfo) or self::tei:recordHist) and (not(self::tei:term) or                 ancestor::tei:binding)"/>
         <assert id="description-elements" test="local-name() = $profile and $placed">&lt;<name/>&gt; isn't one of a manuscript description's elements here. A description holds the profile's elements in their places: the contents and the physical description on a unit, the binding alone on the manuscript, no unit inside a unit; its prose holds only locus, names, title, date, foreign, hi and ref.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-one_ms_singleton_max-80">
      <rule context="tei:msContents|tei:physDesc|tei:history|tei:additional"> <!-- Note: This rule applies to <msContents>, <physDesc>,
             <history>, and <additional> wherever they occur. Luckily
             they are only allowed in places where they are
             constrained to 0 or 1 occurrence. If that changes someday,
             this constraint may will likely need to be updated,
             too. --> <!-- Also worth noting that
             a) if & when we can use abstract patterns, this would be
             better handled as a single abstract rule somewhere, and
             concrete rules in the individual <elementSpec>s; and
             b) I did not test for the existence of "../*[name(.) eq
             $gi][2]" because then an error would be generated for
             each of the multiple occurrences of $gi. -->
         <let name="gi" value="name(.)"/>
         <report test="preceding-sibling::*[ name(.) eq $gi ]                           and                           not( following-sibling::*[ name(.) eq $gi ] )"> Only one &lt;<name/>&gt; is allowed as a child of &lt;<value-of select="name(..)"/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-dimensions-unit-81">
      <rule context="tei:dimensions">
         <assert id="dimensions-unit" test="@unit">Dimensions give their unit (@unit, such as mm).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-duplicateDim-82">
      <rule context="tei:dimensions">
         <report test="count(tei:width) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
         <report test="count(tei:height) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
         <report test="count(tei:depth) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-msId_minimal-83">
      <rule context="tei:msIdentifier">
         <report test="not( parent::tei:msPart )                           and                           ( child::*[1]/self::idno  or  child::*[1]/self::altIdentifier  or  normalize-space(.) eq '')">An &lt;msIdentifier&gt; must contain either a &lt;repository&gt; or &lt;location&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-item-locus-84">
      <rule context="tei:msItem">
         <assert id="item-locus" role="warning" test="tei:locus or tei:locusGrp">An item gives its folios, by locus, or locusGrp for leaves apart, where its source gives them.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-form-term-85">
      <rule context="tei:objectDesc[@form]">
         <let name="terms"
              value="('codex', 'roll', 'sheet', 'faltbuch', 'roll-codex', 'booklet', 'quire',                 'other', 'unknown')"/>
         <assert id="form-term" role="warning" test="@form = $terms">The form <value-of select="@form"/> isn't among the vocabulary's seeds: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-material-term-86">
      <rule context="tei:supportDesc[@material]">
         <let name="terms"
              value="('perg', 'chart', 'papyrus', 'palm', 'mixed', 'other', 'unknown')"/>
         <assert id="material-term" role="warning" test="@material = $terms">The material <value-of select="@material"/> isn't among the vocabulary's seeds: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-decoration-term-87">
      <rule context="tei:decoNote[@type]">
         <let name="terms"
              value="('border', 'diagram', 'illustration', 'initial', 'marginal', 'micrography',                 'miniature', 'drawing', 'rubrication', 'bas-de-page', 'map', 'headpiece', 'canonTable', 'carpetPage',                 'histInit', 'decInit', 'flourInit', 'colInit', 'plainInit', 'chrysography', 'lineFill', 'cadel',                 'instructions', 'unfilled', 'none', 'other', 'foreedge')"/>
         <assert id="decoration-term" role="warning" test="@type = $terms">The decoration <value-of select="@type"/> isn't among the vocabulary's seeds: check its spelling, or add it to the application's vocabulary.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-binding-dated-88">
      <rule context="tei:binding">
         <assert id="binding-dated"
                 test="@contemporary or @when or @notBefore or @notAfter or @from or                 @to">A binding is dated by its bounds, or says whether it is contemporary with the manuscript (@contemporary: true, false, or unknown where nothing is known).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-unit-dated-89">
      <rule context="tei:msPart">
         <assert id="unit-dated"
                 test="tei:history/tei:origin/tei:origDate[@when or @notBefore or @notAfter or                 @from or @to or @type = 'undated']">A unit is dated, in its origin's origDate with its bounds, or said undated (origDate type="undated").</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-linkTargets3-90">
      <rule context="tei:link">
         <assert test="contains(normalize-space(@target),' ')">You must supply at least two values for @target on &lt;<name/>&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-seg-term-declared-91">
      <rule context="tei:seg[@ana]">
         <let name="declared"
              value="/tei:TEI/tei:teiHeader//tei:classDecl//tei:category/@xml:id"/>
         <assert id="seg-term-declared"
                 test="every $t in tokenize(normalize-space(@ana), ' ') satisfies                 (starts-with($t, '#') and substring($t, 2) = $declared)">A segment's term (<value-of select="normalize-space(@ana)"/>) points to a category of a taxonomy in the header's classDecl.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-substContents1-92">
      <rule context="tei:subst">
         <assert test="child::tei:add and (child::tei:del or child::tei:surplus)"> &lt;<name/>&gt; must have at least one child &lt;add&gt; and at least one child &lt;del&gt; or &lt;surplus&gt;.</assert>
      </rule>
   </pattern>
</schema>
