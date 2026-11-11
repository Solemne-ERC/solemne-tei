# SPDX-License-Identifier: MIT
"""Records known and new, registers, authorities that grow, the types of persons and events, and the Bible's file."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.codes import CATEGORIES, code_prefix
from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Problem, Validator

TEI = "http://www.tei-c.org/ns/1.0"


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def fragment(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    """The problems of a fragment, placed in a minimal file as the guide's examples are."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "fragment.xml"
    placed(Example(eg, True, "", "", 1, "fragment.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    return validator.check(path).problems


def whole(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    path = tmp_path / "file.xml"
    path.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<TEI xmlns="{TEI}">{xml}</TEI>', "utf-8")
    return validator.check(path).problems


def rules(found: list[Problem]) -> set[str]:
    return {p.rule for p in found}


def header(formal: str, sources: str = "<p>Made up.</p>") -> str:
    return f"""<teiHeader><fileDesc>
      <titleStmt><title type="formal">{formal}</title></titleStmt>
      <publicationStmt><p>A test.</p></publicationStmt>
      <sourceDesc>{sources}</sourceDesc>
    </fileDesc></teiHeader>"""


REGISTER = '<idno type="type">register</idno>'
DOCUMENT = '<idno>C.EXA-0600</idno><idno type="category">C</idno><idno type="type">edition</idno>'


def register(standoff: str, sources: str = "<p>Made up.</p>") -> str:
    return header(REGISTER, sources) + f"<standOff>{standoff}</standOff>"


IMPRINT = "<imprint><date>1906</date></imprint>"
MS_IDENTIFIER = "<msIdentifier><settlement>München</settlement><idno type='shelfmark'>Clm 4592</idno></msIdentifier>"

KNOWN_AND_NEW = [
    "<person xml:id='PERS.12'><persName type='main'>Deus</persName></person>",
    "<person xml:id='new_person_arno'><persName type='main'>Arno</persName></person>",
    "<personGrp xml:id='PERS.13'><persName type='main'>Romani</persName></personGrp>",
    "<personGrp xml:id='new_person_romans'><persName type='main'>Romani</persName></personGrp>",
    "<place xml:id='PLACE.7'><placeName>Nicaea</placeName></place>",
    "<place xml:id='new_place_mainz'><placeName>Mainz</placeName></place>",
    "<org xml:id='INST.3'><orgName type='main'>BSB</orgName></org>",
    "<org xml:id='new_org_fulda'><orgName type='main'>Fulda</orgName></org>",
    "<event xml:id='EVENT.4'><eventName>Nicaenum</eventName></event>",
    "<event xml:id='new_event_mainz' type='council'><eventName>Moguntinum</eventName></event>",
    f"<listBibl><biblStruct xml:id='PUBL.5'><monogr><title level='m'>Concilia</title>{IMPRINT}</monogr></biblStruct>"
    "</listBibl>",
    f"<listBibl><biblStruct xml:id='new_bibl_mgh'><monogr><title level='m'>Concilia</title>{IMPRINT}</monogr>"
    "</biblStruct></listBibl>",
    "<listBibl><bibl type='work' xml:id='C.NIC-0325'><title>Nicaea</title></bibl></listBibl>",
    "<listBibl><bibl type='version' xml:id='C.NIC-0325-vDIO1'><title>Nicaea</title></bibl></listBibl>",
    "<listBibl><bibl type='work' xml:id='new_work_summa'><title>Summa</title></bibl></listBibl>",
    "<listBibl><bibl type='workGroup' xml:id='GROUP.2'><title>Pseudo-Isidore</title></bibl></listBibl>",
    "<listBibl><bibl type='workGroup' xml:id='new_group_forgeries'><title>Forgeries</title></bibl></listBibl>",
    f"<listBibl><msDesc xml:id='Mun-BSB-4592'>{MS_IDENTIFIER}</msDesc></listBibl>",
]

WRONG_IDS = [
    "<person xml:id='new_place_secunda'><persName type='main'>Secunda</persName></person>",
    "<place xml:id='New_place_Braga'><placeName>Bracara</placeName></place>",
    "<person xml:id='person_7'><persName type='main'>Exemplus</persName></person>",
    "<person><persName type='main'>Exemplus</persName></person>",
    "<person xml:id='solemne_person_7'><persName type='main'>Exemplus</persName></person>",
    "<org xml:id='ORG.1'><orgName type='main'>BSB</orgName></org>",
    "<event xml:id='new_person_mainz' type='council'><eventName>Moguntinum</eventName></event>",
    "<listBibl><bibl type='work' xml:id='nicaea'><title>Nicaea</title></bibl></listBibl>",
    "<listBibl><bibl type='workGroup' xml:id='group_2'><title>Forgeries</title></bibl></listBibl>",
]


@pytest.mark.parametrize("record", KNOWN_AND_NEW)
def test_a_record_s_known_or_new_id_passes(validator: Validator, tmp_path: Path, record: str) -> None:
    assert fragment(validator, tmp_path, record) == []


@pytest.mark.parametrize("record", WRONG_IDS)
def test_an_id_of_neither_form_fails(validator: Validator, tmp_path: Path, record: str) -> None:
    assert "record-id" in rules(fragment(validator, tmp_path, record))


def test_an_edition_in_the_header_is_checked_only_with_an_id(validator: Validator, tmp_path: Path) -> None:
    def edition(biblstruct: str, monogr: str = "") -> str:
        return (
            f"<biblStruct{biblstruct}><monogr{monogr}><title level='m'>Concilia</title>{IMPRINT}</monogr></biblStruct>"
        )

    assert fragment(validator, tmp_path, edition("")) == []
    assert fragment(validator, tmp_path, edition(" xml:id='PUBL.5'")) == []
    assert fragment(validator, tmp_path, edition("", " xml:id='PUBL.6'")) == []
    assert "record-id" in rules(fragment(validator, tmp_path, edition(" xml:id='pertz-1837'")))
    assert "record-id" in rules(fragment(validator, tmp_path, edition("", " xml:id='volume_5'")))


def test_a_known_record_may_hold_its_name_alone_but_not_in_a_register(validator: Validator, tmp_path: Path) -> None:
    person = "<listPerson><person xml:id='PERS.12'><persName type='alternative'>Deus</persName></person></listPerson>"
    assert fragment(validator, tmp_path, person) == []
    assert "person-main-name" in rules(whole(validator, tmp_path, register(person)))


def test_an_event_has_a_type_when_new_or_a_register_s(validator: Validator, tmp_path: Path) -> None:
    def events(xml_id: str) -> str:
        return f"<listEvent><event xml:id='{xml_id}'><eventName>Concilium</eventName></event></listEvent>"

    assert "event-typed" in rules(fragment(validator, tmp_path, events("new_event_concilium")))
    assert fragment(validator, tmp_path, events("EVENT.4")) == []
    assert "event-typed" in rules(whole(validator, tmp_path, register(events("EVENT.4"))))


def test_a_known_manuscript_may_hold_its_identifier_alone(validator: Validator, tmp_path: Path) -> None:
    def manuscript(xml_id: str) -> str:
        return f"<listBibl><msDesc xml:id='{xml_id}'>{MS_IDENTIFIER}</msDesc></listBibl>"

    assert fragment(validator, tmp_path, manuscript("Mun-BSB-4592")) == []
    assert "manuscript-unit" in rules(fragment(validator, tmp_path, manuscript("new_manuscript_munich")))
    assert "manuscript-unit" in rules(whole(validator, tmp_path, register(manuscript("Mun-BSB-4592"))))


PERSON = "<listPerson><person xml:id='PERS.12'><persName type='main'>God</persName></person></listPerson>"
SOURCES = "".join(f"<bibl type='source'><title>List {n}</title></bibl>" for n in range(3))


def test_a_register_with_its_sources_and_no_text_passes(validator: Validator, tmp_path: Path) -> None:
    assert whole(validator, tmp_path, register(PERSON, SOURCES)) == []


def test_a_register_holds_no_text(validator: Validator, tmp_path: Path) -> None:
    xml = header(REGISTER) + "<text><body><p>Textus.</p></body></text>" + f"<standOff>{PERSON}</standOff>"
    assert rules(whole(validator, tmp_path, xml)) == {"register-form"}


def test_a_file_without_a_text_is_a_register(validator: Validator, tmp_path: Path) -> None:
    xml = header(DOCUMENT) + f"<standOff>{PERSON}</standOff>"
    assert rules(whole(validator, tmp_path, xml)) == {"register-form"}


def test_a_register_s_formal_title_holds_its_type_alone(validator: Validator, tmp_path: Path) -> None:
    xml = header('<idno>REG.persons</idno><idno type="type">register</idno>') + f"<standOff>{PERSON}</standOff>"
    assert "formal-title-idnos" in rules(whole(validator, tmp_path, xml))


def test_a_document_still_has_one_source(validator: Validator, tmp_path: Path) -> None:
    xml = header(DOCUMENT, SOURCES) + "<text><body><p>Textus.</p></body></text>"
    assert rules(whole(validator, tmp_path, xml)) == {"text-source-one"}


def person_with(idno: str) -> str:
    return f"<person xml:id='new_person_exemplus'><persName type='main'>Exemplus</persName>{idno}</person>"


MIRABILE = ["mirabileAuthor", "mirabilePerson", "mirabileWork", "mirabileManuscript", "mirabilePlace"]
SEEDS = ["isil", "doi", "k10plus", "dnb", "openAlex", "gryson", "kery", "whg", "jaffe", "wikidata", *MIRABILE]


@pytest.mark.parametrize("authority", SEEDS)
def test_an_authority_the_guide_lists_passes(validator: Validator, tmp_path: Path, authority: str) -> None:
    assert fragment(validator, tmp_path, person_with(f"<idno type='{authority}'>1</idno>")) == []


def test_an_authority_the_guide_doesn_t_list_is_reported_not_refused(validator: Validator, tmp_path: Path) -> None:
    found = fragment(validator, tmp_path, person_with("<idno type='regestaImperii'>1</idno>"))
    assert [(p.rule, p.severity) for p in found] == [("authority-term", "warning")]


def test_mirabile_s_single_key_is_reported_since_its_indices_are_authorities(
    validator: Validator, tmp_path: Path
) -> None:
    found = fragment(validator, tmp_path, person_with("<idno type='mirabile'>19840</idno>"))
    assert [(p.rule, p.severity) for p in found] == [("authority-term", "warning")]


@pytest.mark.parametrize(
    ("target", "reported"),
    [
        ("https://www.mirabileweb.it/search-person/-person/1044/77", True),
        ("https://www.mirabileweb.it/search-place/-place/1044/6074", True),
        ("https://www.mirabileweb.it/title/-title/20174", True),
        ("https://www.vhmml.org/readingRoom/view/12345", True),
        ("https://data.biblissima.fr/w/Item:Q12345", True),
        ("https://portail.biblissima.fr/fr/ark:/43093/mdata0123", True),
        ("https://portail.biblissima.fr/ark:/43093/mdata0123", True),
        ("https://iiif.biblissima.fr/collections/manifest/0123abc", False),
        ("https://example.org/a-page-about-it", False),
    ],
)
def test_an_authority_s_record_given_as_a_link_is_reported(
    validator: Validator, tmp_path: Path, target: str, reported: bool
) -> None:
    links = f"<note type='links'><list type='links'><item><ref target='{target}'>A page</ref></item></list></note>"
    assert ("link-authority" in rules(fragment(validator, tmp_path, person_with(links)))) == reported


def test_a_declared_authority_passes(validator: Validator, tmp_path: Path) -> None:
    declaration = (
        "<category xml:id='regestaImperii'><catDesc>Regesta Imperii "
        "<ptr target='https://example.org/ri/$1'/></catDesc></category>"
    )
    found = fragment(validator, tmp_path, declaration + person_with("<idno type='regestaImperii'>1</idno>"))
    assert found == []


@pytest.mark.parametrize("kind", ["person", "work", "manuscript"])
def test_an_authority_s_link_may_be_typed_by_the_record_s_kind(validator: Validator, tmp_path: Path, kind: str) -> None:
    category = f"<category xml:id='catalogus'><catDesc>C <ptr type='{kind}' target='https://e.org/{kind}/$1'/></catDesc></category>"
    assert fragment(validator, tmp_path, category) == []


def test_an_authority_s_link_holds_the_id_s_place(validator: Validator, tmp_path: Path) -> None:
    category = "<category xml:id='catalogus'><catDesc>C <ptr target='https://example.org/'/></catDesc></category>"
    assert rules(fragment(validator, tmp_path, category)) == {"authority-link"}


@pytest.mark.parametrize(
    ("record", "rule", "flagged"),
    [
        ("<person xml:id='new_person_deus' type='divine'><persName type='main'>Deus</persName></person>", "", False),
        (
            "<person xml:id='new_person_paulus' type='saint'><persName type='main'>Paulus</persName></person>",
            "person-term",
            True,
        ),
        ("<event xml:id='new_event_x' type='synod'><eventName>Synodus</eventName></event>", "", False),
        ("<event xml:id='new_event_y' type='councel'><eventName>Synodus</eventName></event>", "event-term", True),
        (
            "<listBibl><bibl type='workGroup' subtype='derivedCollections' xml:id='new_group_a'><title>A</title>"
            "</bibl></listBibl>",
            "",
            False,
        ),
        (
            "<listBibl><bibl type='workGroup' subtype='sameOrigin' xml:id='new_group_b'><title>B</title>"
            "</bibl></listBibl>",
            "work-group-term",
            True,
        ),
    ],
)
def test_a_type_outside_the_seeds_is_reported(
    validator: Validator, tmp_path: Path, record: str, rule: str, flagged: bool
) -> None:
    found = fragment(validator, tmp_path, record)
    assert [(p.rule, p.severity) for p in found] == ([(rule, "warning")] if flagged else [])


@pytest.mark.parametrize(("whole", "part"), [("GROUP.2", "GROUP.3"), ("new_group_letters", "new_group_register")])
def test_a_group_points_to_the_larger_one_it_is_a_part_of(
    validator: Validator, tmp_path: Path, whole: str, part: str
) -> None:
    groups = (
        f"<listBibl><bibl type='workGroup' xml:id='{whole}'><title>Letters</title></bibl>"
        f"<bibl type='workGroup' xml:id='{part}' corresp='#{whole}'><title>Register</title></bibl></listBibl>"
    )
    assert fragment(validator, tmp_path, groups) == []


@pytest.mark.parametrize(
    "record",
    [
        "<bibl type='workGroup' xml:id='GROUP.3' corresp='#PERS.12'><title>Register</title></bibl>",
        "<bibl type='workGroup' xml:id='GROUP.3' corresp='#GROUP.2 #PERS.12'><title>Register</title></bibl>",
        "<bibl type='work' xml:id='C.NIC-0325' corresp='#GROUP.2'><title>Nicaea</title></bibl>",
    ],
)
def test_only_a_work_group_s_corresp_to_groups_is_left_alone(validator: Validator, tmp_path: Path, record: str) -> None:
    assert rules(fragment(validator, tmp_path, f"<listBibl>{record}</listBibl>")) == {"record-pointer-in-ref"}


def memberships(*places: tuple[str, str]) -> str:
    """Members of work groups, each a group's pointer and a place."""
    relations = "".join(
        f"<relation name='memberOf' type='judgement' active='D.EXE-0601-{i}' passive='{group}' n='{n}'/>"
        for i, (group, n) in enumerate(places, 1)
    )
    return f"<listRelation>{relations}</listRelation>"


@pytest.mark.parametrize("n", ["1", "12"])
def test_a_member_s_place_is_a_whole_number_from_1(validator: Validator, tmp_path: Path, n: str) -> None:
    assert fragment(validator, tmp_path, memberships(("#GROUP.12", n))) == []


@pytest.mark.parametrize("n", ["0", "01", "x", "1.2"])
def test_a_place_of_another_form_is_reported(validator: Validator, tmp_path: Path, n: str) -> None:
    found = fragment(validator, tmp_path, memberships(("#GROUP.12", n)))
    assert [(p.rule, p.severity) for p in found] == [("member-place-number", "warning")]


def test_two_members_of_one_group_at_one_place_are_both_reported(validator: Validator, tmp_path: Path) -> None:
    found = fragment(validator, tmp_path, memberships(("#GROUP.12", "1"), ("#GROUP.12", "2"), ("#GROUP.12", "1")))
    assert [(p.rule, p.severity) for p in found] == [("member-place-unique", "warning")] * 2


def test_members_of_two_groups_may_share_a_place(validator: Validator, tmp_path: Path) -> None:
    assert fragment(validator, tmp_path, memberships(("#GROUP.12", "1"), ("#new_group_letters", "1"))) == []


def test_a_place_on_a_person_s_membership_is_not_checked(validator: Validator, tmp_path: Path) -> None:
    relation = "<listRelation><relation name='memberOf' active='#PERS.22' passive='#PERS.21' n='x'/></listRelation>"
    assert fragment(validator, tmp_path, relation) == []


@pytest.mark.parametrize(
    ("name", "reported"),
    [
        ("holdsOfficeIn", True),
        ("referencedIn", True),
        ("hasRole", False),
        ("memberOf", False),
        ("isLongerVersionOf", False),
        ("closeRenderingOf", False),
    ],
)
def test_the_relation_types_to_start_with(validator: Validator, tmp_path: Path, name: str, reported: bool) -> None:
    relation = f"<relation name='{name}' active='#new_person_a' passive='#new_person_b'/>"
    assert ("relation-term" in rules(fragment(validator, tmp_path, relation))) == reported


def test_the_bible_is_a_category_its_own_prefix() -> None:
    assert "BIB" in CATEGORIES and code_prefix("BIB") == "BIB"


def test_the_vulgate_s_code_passes(validator: Validator, tmp_path: Path) -> None:
    title = (
        '<title type="formal"><idno>BIB.Vulg</idno><idno type="category">BIB</idno>'
        '<idno type="type">edition</idno></title>'
    )
    assert fragment(validator, tmp_path, title) == []


def test_a_book_is_a_section_with_its_code(validator: Validator, tmp_path: Path) -> None:
    book = """<div type="section" n="MAT"><head type="rubric">Evangelium secundum Matthaeum</head>
      <div type="chapter" n="18"><div type="chapter" n="19"><p>Iterum dico vobis.</p></div></div></div>"""
    assert fragment(validator, tmp_path, book) == []


def test_a_book_s_code_stands_only_on_a_section(validator: Validator, tmp_path: Path) -> None:
    assert rules(fragment(validator, tmp_path, '<div type="chapter" n="JOH"><p>In principio.</p></div>')) == {
        "book-code-section"
    }


def test_n_takes_no_name_but_a_book_s_code(validator: Validator, tmp_path: Path) -> None:
    found = fragment(validator, tmp_path, '<div type="section" n="XYZ"><p>In principio.</p></div>')
    assert {p.check for p in found} == {"relaxng"}


def test_a_record_s_literature_is_an_untyped_bibl_in_it(validator: Validator, tmp_path: Path) -> None:
    person = """<person xml:id="new_person_exemplus"><persName type="main">Exemplus</persName>
      <bibl><ptr target="#PUBL.5"/><citedRange unit="page" from="112" to="114">112–114</citedRange>, as
        "Exemplus episcopus"</bibl></person>"""
    assert fragment(validator, tmp_path, person) == []


def test_a_known_work_stands_for_its_canonical_version(validator: Validator, tmp_path: Path) -> None:
    works = """<listBibl>
        <bibl type="work" xml:id="C.NIC-0325"><title>Nicaea</title><idno>C.NIC-0325</idno>
          <ptr type="stand-in" target="#C.NIC-0325-vDIO1"/></bibl>
        <bibl type="version" xml:id="C.NIC-0325-vDIO1"><title>Nicaea, Dionysiana</title>
          <idno>C.NIC-0325-vDIO1</idno></bibl>
      </listBibl>
      <listRelation><relation name="versionOf" active="#C.NIC-0325-vDIO1" passive="#C.NIC-0325"/></listRelation>"""
    assert whole(validator, tmp_path, register(works)) == []


def test_a_book_s_prologue_is_a_preface_before_its_first_chapter(validator: Validator, tmp_path: Path) -> None:
    book = """<div type="section" n="SIR"><head type="rubric">Ecclesiasticus</head>
      <div type="preface"><head type="rubric">Prologus.</head><p>Multorum nobis et magnorum.</p></div>
      <div type="chapter" n="1"><div type="chapter" n="1"><p>Omnis sapientia a Domino Deo est.</p></div>
        <div type="chapter" n="2"><p>Arenam maris quis dinumeravit?</p></div></div></div>"""
    assert fragment(validator, tmp_path, book) == []
