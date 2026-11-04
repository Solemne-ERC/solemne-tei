<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: MIT -->
<!-- Generated from solemne.odd 0.1.0 (SHA-256 6e1bc4d866801a6c5df7f525d1a08633adf48a5a53591338c0797d8faf3222a0) by solemne-tei build. Edit the ODD, not this file. -->
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

Its manuscript description module comes from the Bodleian Libraries' consolidated TEI schema (https://github.com/msDesc/consolidated-tei-schema, commit 7e8b89c), under its licence:

BSD 2-Clause License

Copyright (c) 2017, James Cummings
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
   <!-- ******************************************************* -->
   <!-- constraints in en, und, mul, zxx, of which there are 94 -->
   <!-- ******************************************************* -->
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
   <pattern id="schematron-constraint-fragments-12">
      <rule context="tei:*[@next]">
         <let name="next"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@next), '#')]"/>
         <assert id="fragment-next"
                 test="count($next) = 1 and local-name($next) = local-name() and                   normalize-space($next/@prev) = concat('#', @xml:id)">&lt;<name/>&gt;'s @next (<value-of select="@next"/>) points to the next fragment in the file, a &lt;<name/>&gt; whose @prev points back.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-fragments-13">
      <rule context="tei:*[@prev]">
         <let name="prev"
              value="//tei:*[@xml:id = substring-after(normalize-space(current()/@prev), '#')]"/>
         <assert id="fragment-prev"
                 test="count($prev) = 1 and local-name($prev) = local-name() and                   normalize-space($prev/@next) = concat('#', @xml:id)">&lt;<name/>&gt;'s @prev (<value-of select="@prev"/>) points to the previous fragment in the file, a &lt;<name/>&gt; whose @next points back.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-deprecationInfo-only-in-deprecated-14">
      <rule context="tei:desc[ @type eq 'deprecationInfo']">
         <assert test="../@validUntil">Information about a deprecation should only be present in a specification element that is being deprecated: that is, only an element that has a @validUntil attribute should have a child &lt;desc type="deprecationInfo"&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-gap-extent-15">
      <rule context="tei:gap[@quantity or @unit]">
         <assert id="gap-quantity-unit" test="@quantity and @unit">A gap's quantity is given with its unit (leaves, lines, words or chars), and a unit with its quantity.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-ptrAtts-16">
      <rule context="tei:ptr">
         <report test="@target and @cRef">Only one of the attributes @target and @cRef may be supplied on &lt;<name/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-refAtts-17">
      <rule context="tei:ref">
         <report test="@target and @cRef">Only one of the attributes @target and @cRef may be supplied on &lt;<name/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-gloss-list-must-have-labels-18">
      <rule context="tei:list[@type='gloss']">
         <assert test="tei:label"> The content of a "gloss" list should include a sequence of one or more pairs of a &lt;label&gt; element followed by an &lt;item&gt; element.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-dates-19">
      <rule context="tei:*[@notBefore or @notAfter][not(self::tei:locus or self::tei:biblScope or                 self::tei:citedRange)]">
         <assert id="date-span-bounds"
                 role="warning"
                 test="@notBefore and @notAfter">A span gives both its bounds, @notBefore and @notAfter.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-dates-20">
      <rule context="tei:*[@from or @to][not(self::tei:locus or self::tei:biblScope or                 self::tei:citedRange)]">
         <assert id="date-from-to" role="warning" test="@from and @to">A span gives both its ends, @from and @to.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-record-pointers-21">
      <rule context="tei:*[@key or @corresp]">
         <report id="record-pointer-in-ref"
                 role="warning"
                 test="some $p in tokenize(normalize-space(string-join((@key, @corresp), ' ')), ' ') satisfies matches($p, '^#?[Nn]ew_[A-Za-z]+_|^#?(PERS\.\d+|solemne_person_\d+)$|^https?://\S+/id/(person|place|institution|event|manuscript|publication)/')">&lt;<name/>&gt; points to a record in @key or @corresp (<value-of select="normalize-space(string-join((@key,                   @corresp), ' '))"/>): a record is pointed to by @ref, on a name inside provenance, acquisition and origin.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-statement-22">
      <rule context="tei:fileDesc/tei:titleStmt">
         <assert id="title-first-formal" test="tei:title[1][@type = 'formal']">The title statement opens with a title typed formal.</assert>
         <assert id="title-one-formal" test="count(tei:title[@type = 'formal']) = 1">The title statement has one formal title.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-title-statement-23">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title">
         <assert id="title-type" test="@type = ('formal', 'alias', 'other')">A title in the title statement is typed formal, alias or other.</assert>
         <assert id="title-alias-words"
                 test="not(@type = 'alias') or normalize-space(.) != ''">An alias isn't empty.</assert>
         <assert id="title-other-source"
                 role="warning"
                 test="not(@type = 'other') or @source">A title typed other names its source in @source.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-24">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']">
         <assert id="formal-title-idnos"
                 test="count(tei:idno[not(@type)]) = 1 and count(tei:idno[@type =                   'category']) = 1 and count(tei:idno[@type = 'type']) = 1 and (every $level in ('work', 'version',                   'witness', 'transcription') satisfies count(tei:idno[@type = $level]) le 1)">The formal title holds the document's code (an identifier without a type), its category and its type, once each, and at most one permalink for each level the file belongs to.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-25">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title/tei:idno">
         <assert id="idno-in-formal-title" test="parent::tei:title[@type = 'formal']">An identifier in the title statement stands in the formal title.</assert>
         <assert id="idno-type"
                 test="not(@type) or @type = ('category', 'type', 'work', 'version',                   'witness', 'transcription')">An identifier in the formal title is the code (without a type), the category, the type, or the permalink of a level (work, version, witness, transcription).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-26">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[not(@type)]">
         <let name="category"
              value="normalize-space(../tei:idno[@type = 'category'][1])"/>
         <let name="prefix" value="substring-before(normalize-space(.), '.')"/>
         <assert id="code-format"
                 test="matches(normalize-space(.),                   '^[A-Z]+\.[A-Za-z0-9]+([.\-][A-Za-z0-9]+)*$')">The document's code (<value-of select="normalize-space(.)"/>) begins with its category's prefix and a dot, and holds only letters, digits, dots and hyphens.</assert>
         <assert id="code-category"
                 test="$category = ('', 'UNK', 'LR', 'CPT', 'CHA') or $prefix = (if                   ($category = ('SYSCOLL', 'CHRCOLL')) then 'COLL' else $category)">The document's code (<value-of select="normalize-space(.)"/>) begins with its category's prefix (<value-of select="if ($category = ('SYSCOLL', 'CHRCOLL')) then 'COLL' else $category"/>, for the category <value-of select="$category"/>).</assert>
         <assert id="code-manuscript"
                 test="not(contains(normalize-space(.), '.ms-')) or                   ancestor::tei:fileDesc/tei:sourceDesc//tei:msDesc">A manuscript's code (<value-of select="normalize-space(.)"/>) goes with the manuscript's description (msDesc) in the sourceDesc.</assert>
         <assert id="code-matches-file-name"
                 role="warning"
                 test="not(matches(base-uri(.),                   '/(C|D|COLL|P|EP|H|EX)\.[^/]*\.xml$')) or ends-with(base-uri(.), concat('/',                   encode-for-uri(normalize-space(.)), '.xml'))">A file named by a code is named by its document's code (<value-of select="normalize-space(.)"/>).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-27">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[@type = 'category']">
         <assert id="category-value"
                 test="normalize-space(.) = ('SYSCOLL', 'CHRCOLL', 'C', 'D', 'P', 'H',                   'EX', 'EP', 'LR', 'CPT', 'CHA', 'UNK')">The document's category (<value-of select="normalize-space(.)"/>) is one of SYSCOLL, CHRCOLL, C, D, P, H, EX, EP, LR, CPT, CHA, UNK.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-formal-title-28">
      <rule context="tei:fileDesc/tei:titleStmt/tei:title[@type = 'formal']/tei:idno[@type = 'type']">
         <assert id="document-type-value"
                 test="normalize-space(.) = ('edition', 'manuscript',                   'reconstruction', 'hypothesis', 'placeholder')">The document's type (<value-of select="normalize-space(.)"/>) is one of edition, manuscript, reconstruction, hypothesis, placeholder.</assert>
         <assert id="type-manuscript"
                 test="not(normalize-space(.) = 'manuscript') or                   ancestor::tei:fileDesc/tei:sourceDesc//tei:msDesc">A document typed manuscript has the manuscript's description (msDesc) in its sourceDesc.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-declarations-29">
      <rule context="tei:*[@decls]">
         <assert id="decls-target"
                 test="every $t in tokenize(normalize-space(@decls), ' ') satisfies                   (starts-with($t, '#') and exists(/tei:TEI/tei:teiHeader//(tei:correction |                   tei:segmentation)[@xml:id = substring($t, 2)]))">@decls (<value-of select="normalize-space(@decls)"/>) points to a correction or a segmentation in the header.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-declarations-30">
      <rule context="tei:editorialDecl[count(tei:correction) gt 1]">
         <assert id="correction-default"
                 test="count(tei:correction[@default = 'true']) = 1">Of several corrections, one is the default (@default="true"): the whole text's.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-declarations-31">
      <rule context="tei:segmentation[@type = 'inferred-units'][@default = 'false']">
         <let name="id" value="concat('#', @xml:id)"/>
         <assert id="inferred-units-pointed-to"
                 role="warning"
                 test="@xml:id and                   //@decls[tokenize(normalize-space(.), ' ') = $id]">A statement of inferred units for some divisions (@default="false") is pointed to by their @decls.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-quotationContents-32">
      <rule context="tei:quotation">
         <report test="not( @marks )  and  not( tei:p )"> On &lt;<name/>&gt;, either the @marks attribute should be used, or a paragraph of description provided.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-citestructure-outer-match-33">
      <rule context="tei:citeStructure[not(parent::tei:citeStructure)]">
         <assert test="starts-with(@match,'/')">An XPath in @match on the outer &lt;<name/>&gt; must start with '/'.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-citestructure-inner-match-34">
      <rule context="tei:citeStructure[parent::tei:citeStructure]">
         <assert test="not(starts-with(@match,'/'))">An XPath in @match must not start with '/' except on the outer &lt;<name/>&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-same-as-prefixes-35">
      <rule context="tei:*[@sameAs]">
         <let name="declared" value="/tei:TEI/tei:teiHeader//tei:prefixDef/@ident"/>
         <assert id="same-as-prefix-declared"
                 test="every $id in tokenize(normalize-space(@sameAs), ' ')                   satisfies (not(matches($id, '^[A-Za-z][A-Za-z0-9+.\-]*:')) or matches($id, '^https?:') or                   substring-before($id, ':') = $declared)">The prefixes in @sameAs (<value-of select="normalize-space(@sameAs)"/>) are declared in the header, by prefixDef in listPrefixDef.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-same-as-prefixes-36">
      <rule context="tei:prefixDef">
         <assert id="prefix-known"
                 role="warning"
                 test="@ident = ('scta', 'clavis', 'pseudoisidor',                   'corpuscorporum')">The prefix <value-of select="@ident"/> isn't one the application knows (scta, clavis, pseudoisidor, corpuscorporum).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-text-elements-37">
      <rule context="tei:body//tei:*">
         <assert id="text-elements"
                 test="local-name() = ('div', 'head', 'p', 'note', 'pb', 'lb', 'gap',                   'persName', 'placeName', 'eventName', 'bibl', 'cit', 'quote', 'ref', 'seg', 'date', 'subst',                   'add', 'del', 'unclear', 'foreign', 'choice', 'corr', 'sic', 'abbr', 'expan', 'supplied', 'rs',                   'anchor')">&lt;<name/>&gt; isn't one of the text's elements.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-text-note-type-38">
      <rule context="tei:body//tei:note">
         <assert id="text-note-type" test="@type = ('source', 'parallel', 'editorial')">A note in the text is typed source, parallel or editorial.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-note-has-content-39">
      <rule context="tei:note">
         <assert id="note-has-content" test="normalize-space(.) != '' or @source or *">A note holds words, or its codes in @source.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-source-note-codes-40">
      <rule context="tei:body//tei:note[@type = 'source']">
         <report id="source-note-codes"
                 role="warning"
                 test="some $w in tokenize(normalize-space(.), '[\s;,]+')                   satisfies matches($w, '^(cf_)?((C|D|COLL|P|EP|H|EX|W)\.[A-Za-z0-9.\-]+(_[A-Za-z0-9.\-]+)?|[1-4]?[A-Z]{2,4}_[0-9]+(_[0-9]+)?(-[0-9]+)?)$')">A source note's words hold a code (<value-of select="normalize-space(.)"/>): it belongs in @source.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-unit-alone-41">
      <rule context="tei:div[@type = 'unit']">
         <assert id="unit-alone" test="count(../tei:div) gt 1">A unit stands alone in its division: its paragraphs belong to the division itself.</assert>
         <assert id="unit-holds-text" test="not(tei:div) and not(tei:head)">A unit holds paragraphs only, without headings or divisions.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-register-item-in-register-42">
      <rule context="tei:div[@type = 'registerItem']">
         <assert id="register-item-in-register"
                 test="parent::tei:div[@type = 'register']">A register item stands in a register.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-number-heading-n-43">
      <rule context="tei:div[tei:head[@type = 'number']]">
         <assert id="number-heading-n" test="@n">A division with a number heading (<value-of select="normalize-space(tei:head[@type = 'number'][1])"/>) has @n.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-div-in-l-44">
      <rule context="tei:l//tei:div">
         <assert test="ancestor::tei:floatingText"> Abstract model violation: Metrical lines (&lt;l&gt; elements) may not contain higher-level structural elements such as &lt;div&gt;, unless &lt;div&gt; is a descendant of &lt;floatingText&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-abstractModel-structure-div-in-ab-or-p-45">
      <rule context="tei:div">
         <report test="(ancestor::tei:p or ancestor::tei:ab) and not(ancestor::tei:floatingText)"> Abstract model violation: &lt;p&gt; and &lt;ab&gt; may not contain higher-level structural elements such as &lt;div&gt;, unless &lt;div&gt; is a descendant of &lt;floatingText&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-event-content-46">
      <rule context="tei:event">
         <assert id="event-described" test="@ref or tei:eventName or tei:p">An event points to a record (@ref) or describes one, with eventName or p.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-event-content-47">
      <rule context="tei:event/tei:desc | tei:event/tei:p">
         <assert id="event-words" test="normalize-space(.) != ''">An event's description isn't empty.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-floruit-dates-48">
      <rule context="tei:floruit">
         <assert id="floruit-dates"
                 test="@when or @notBefore or @notAfter or @from or @to or                   @period">A floruit gives its dates in its attributes.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-standoff-person-49">
      <rule context="tei:standOff//tei:listPerson/tei:person">
         <assert id="person-id"
                 test="matches(@xml:id, '^(PERS\.\d+|solemne_person_\d+|new_person_\S+)$')">A person in the standOff has an @xml:id: a record's (PERS. and a number, or solemne_person_ and a number), or a placeholder's (new_person_ and a name).</assert>
         <assert id="person-main-name"
                 test="count(tei:persName[@type = 'main']) = 1 or                   not(starts-with(@xml:id, 'new_person_'))">A new person has one main name (persName typed main).</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-standoff-person-50">
      <rule context="tei:standOff//tei:note[@type = 'links']">
         <assert id="links-list"
                 test="tei:list[@type = 'links'] and not(text()[normalize-space()])">A note of links holds a list of links, and no words of its own.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-standoff-person-51">
      <rule context="tei:standOff//tei:list[@type = 'links']/tei:item">
         <assert id="link-target" test="tei:ref[@target][normalize-space(.) != '']">A link has a @target and words.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-ref-or-key-or-name-52">
      <rule context="tei:relation">
         <assert test="@ref or @key or @name">One of the attributes @name, @ref or @key must be supplied.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-active-mutual-53">
      <rule context="tei:relation">
         <report test="@active and @mutual">Only one of the attributes @active and @mutual may be supplied.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-active-passive-54">
      <rule context="tei:relation">
         <report test="@passive and not(@active)">the attribute @passive may be supplied only if the attribute @active is supplied.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-manuscript-units-55">
      <rule context="tei:msDesc">
         <assert id="manuscript-unit" test="tei:msPart">A manuscript's description has at least one codicological unit (msPart), with its own identifier: the unit holds the physical description, the date, the hands and the decoration.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-one_ms_singleton_max-56">
      <rule context="tei:msContents|tei:physDesc|tei:history|tei:additional">
         <let name="gi" value="name(.)"/>
         <report test="preceding-sibling::*[ name(.) eq $gi ]                           and                           not( following-sibling::*[ name(.) eq $gi ] )"> Only one &lt;<name/>&gt; is allowed as a child of &lt;<value-of select="name(..)"/>&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-catchword_in_msDesc-57">
      <rule context="tei:catchwords">
         <assert test="ancestor::tei:msDesc or ancestor::tei:egXML">The &lt;<name/>&gt; element should not be used outside of &lt;msDesc&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-dimensions-unit.check-58">
      <rule context="//tei:dimensions">
         <assert test="@unit" role="error"> The unit of measurement must be specified in the unit attribute on the dimensions element</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-duplicateDim-59">
      <rule context="tei:dimensions">
         <report test="count(tei:width) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
         <report test="count(tei:height) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
         <report test="count(tei:depth) gt 1"> The element &lt;<name/>&gt; may appear once only.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-origDate.check-60">
      <rule context="//tei:origDate">
         <assert test="@calendar and (@when or @notBefore or @notAfter or @from or @to) and string-length(normalize-space(string())) gt 0"
                 role="error"> The origDate element must have two or more attributes - calendar and at least one of when, notBefore, notAfter, from and/or to - and must contain some text describing the date.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-secFol_in_msDesc-61">
      <rule context="tei:secFol">
         <assert test="ancestor::tei:msDesc or ancestor::tei:egXML">The &lt;<name/>&gt; element should not be used outside of &lt;msDesc&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-signatures_in_msDesc-62">
      <rule context="tei:signatures">
         <assert test="ancestor::tei:msDesc or ancestor::tei:egXML">The &lt;<name/>&gt; element should not be used outside of &lt;msDesc&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-msId_minimal-63">
      <rule context="tei:msIdentifier">
         <report test="not( parent::tei:msPart )                           and                           ( child::*[1]/self::idno  or  child::*[1]/self::altIdentifier  or  normalize-space(.) eq '')">An &lt;msIdentifier&gt; must contain either a &lt;repository&gt; or &lt;location&gt;.</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-textLang.check-64">
      <rule see="https://msdesc.github.io/consolidated-tei-schema/msdesc.html#objectdescBook"
            context="//tei:sourceDesc/tei:msDesc[not(tei:msPart)]">
         <assert test="tei:physDesc/tei:objectDesc[@form]" role="warn"> The physical form of the carrier should be recorded in the objectDesc element, with a form attribute.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-textLang.check-65">
      <rule context="//tei:sourceDesc/tei:msDesc/tei:msPart">
         <assert test="                                         tei:physDesc/tei:objectDesc[@form]                                         or ancestor::tei:msDesc/tei:physDesc/tei:objectDesc[@form]                                         "
                 role="warn"> The physical form of the carrier should be recorded in the objectDesc element, with a form attribute, unless it has been described for the entire manuscript.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-textLang.check-66">
      <rule see="https://msdesc.github.io/consolidated-tei-schema/msdesc.html#supportdesc"
            context="//tei:sourceDesc/tei:msDesc[not(tei:msPart)]">
         <assert test="tei:physDesc/tei:objectDesc/tei:supportDesc[@material]"
                 role="warn"> The material (parchment, paper, etc.) of a manuscript should be recorded in the supportDesc element, with a material attribute.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-textLang.check-67">
      <rule context="//tei:sourceDesc/tei:msDesc/tei:msPart">
         <assert test="                                             tei:physDesc/tei:objectDesc/tei:supportDesc[@material]                                             or ancestor::tei:msDesc/tei:physDesc/tei:objectDesc/tei:supportDesc[@material]                                             "
                 role="warn"> The material (parchment, paper, etc.) of each part should be recorded in the supportDesc element, with a material attribute, unless it has been described for the entire manuscript.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-binding.check-68">
      <rule context="//tei:binding">
         <assert test="@when or @notBefore or @notAfter or @contemporary='true'"
                 role="warn"> The binding element should have dating attributes (when or notBefore/notAfter) or a contemporary attribute (with the value 'true').</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-facsimile.warn-69">
      <rule context="//tei:surrogates/tei:bibl">
         <report test="contains(@type, 'fascimile')" role="warn"> The type attribute of "<value-of select="@type"/>" contains a typo (fascimile should be facsimile).</report>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-linkTargets3-70">
      <rule context="tei:link">
         <assert test="contains(normalize-space(@target),' ')">You must supply at least two values for @target on &lt;<name/>&gt;.</assert>
      </rule>
   </pattern>
   <pattern id="schematron-constraint-substContents1-71">
      <rule context="tei:subst">
         <assert test="child::tei:add and (child::tei:del or child::tei:surplus)"> &lt;<name/>&gt; must have at least one child &lt;add&gt; and at least one child &lt;del&gt; or &lt;surplus&gt;.</assert>
      </rule>
   </pattern>
</schema>
