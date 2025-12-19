from pyparsing import (
    Combine,
    DelimitedList,
    Group,
    LineEnd,
    Literal,
    MatchFirst,
    OneOrMore,
    Regex,
    SkipTo,
    White,
    ZeroOrMore,
    rest_of_line,
    token_map,
)

from . import common


def ChangeLogDocument():
    initialState = (
        IntroSection()("intro")
        + common.maybeLineEndings()
        + UnifiedReleases()("releases")
        + common.maybeLineEndings()
    )
    afterReleaseState = (
        IntroSection()("intro")
        + common.maybeLineEndings()
        + UnifiedReleases()("releases")
        + common.maybeLineEndings()
        + OneOrMore(ReleaseReferencesSection())("references")
        + common.maybeLineEndings()
    )
    return Group(MatchFirst([afterReleaseState(), initialState()]))


# First Level Parsers


def IntroSection():
    return (
        common.h1()
        + Literal("Changelog")
        + LineEnd()
        + Literal(
            "All notable changes to this project will be documented in this file."
        )
        + LineEnd()
        + Literal(
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),"
        )
        + LineEnd()
        + Literal(
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)."
        )
        + LineEnd()
    )


def UnifiedReleases():
    unified = UnreleasedSection() | ReleaseSection()
    return Group(OneOrMore(unified() + common.maybeLineEndings()))("release")


def ReleaseReferencesSection():
    reference = UnreleasedReference() | ReleaseReference()
    return DelimitedList(reference(), LineEnd())


# Second Level Parsers


def UnreleasedSection():
    return Group(
        Combine(UnreleasedHeading())("version")
        + common.maybeLineEndings().suppress()
        + ZeroOrMore(ChangeTypeSection())("change_types")
        + common.maybeLineEndings().suppress()
    )


def ReleaseSection():
    return Group(
        Combine(ReleaseHeading())
        + common.maybeLineEndings().suppress()
        + OneOrMore(ChangeTypeSection())("change_types")
        + common.maybeLineEndings().suppress()
    )


def UnreleasedReference():
    version = Combine(
        common.openB().suppress()
        + Literal("Unreleased")
        + common.closeB().suppress()
        + Literal(":").suppress()
    )
    return Group(version()("version") + ReferenceLink()("link"))


def ReleaseReference():
    version = Combine(
        common.openB().suppress()
        + Combine(SkipTo(common.closeB()))
        + common.closeB().suppress()
        + Literal(":").suppress()
    )
    return Group(version()("version") + ReferenceLink()("link"))


# Third Level Parsers


def UnreleasedHeading():
    return Group(
        common.h2().suppress()
        + common.openB().suppress()
        + Literal("Unreleased")
        + common.closeB().suppress()
        + common.trailingWhiteSpace().suppress()
        + LineEnd().suppress()
    )


def ReleaseHeading():
    version = Combine(
        common.openB().suppress() + SkipTo(common.closeB()) + common.closeB().suppress()
    )
    date = Combine(Literal(" - ").suppress() + Regex(r"\d{4}-\d{2}-\d{2}"))
    return Combine(
        common.h2().suppress()
        + version()("version")
        + date()("release_date")
        + common.trailingWhiteSpace().suppress()
        + LineEnd()
    )


def ChangeTypeSection():
    return Group(
        Combine(ChangeTypeHeading())("type")
        + common.maybeLineEndings().suppress()
        + ChangeEntries()("entries")
        + LineEnd().suppress()
    )


def ReferenceLink():
    return Combine(
        common.openAB().suppress()
        + SkipTo(common.closeAB())
        + common.closeAB().suppress()
        + common.trailingWhiteSpace().suppress()
    )


# Fourth Level Parsers


def ChangeTypeHeading():
    changeType = (
        Literal("Added")
        | Literal("Changed")
        | Literal("Fixed")
        | Literal("Removed")
        | Literal("Security")
    )
    return (
        common.h3().suppress()
        + changeType()
        + common.trailingWhiteSpace().suppress()
        + LineEnd().suppress()
    )


def ChangeEntries():
    return OneOrMore(ChangeEntry())


# Fifth Level Parsers


def ChangeEntry():
    def post_process(x, y, tokens):
        description = SkipTo(Link()).set_parse_action(token_map(str.strip))
        withLink = description()("description") + Link()("link")
        withoutLink = (rest_of_line()("description")).set_parse_action(
            token_map(str.strip)
        )

        return (MatchFirst([withLink(), withoutLink()])).parse_string(tokens[0])

    preProcessedEntry = (
        Literal("-").suppress() + ZeroOrMore(White()).suppress() + rest_of_line()
    )
    processedEntry = preProcessedEntry().set_parse_action(post_process)
    return Group(processedEntry())


### Sixth Level Parsers


def Link():
    return Group(
        common.openB
        + SkipTo(common.closeB())("text")
        + common.closeB()
        + common.openP()
        + SkipTo(common.closeP())("href")
        + common.closeP()
        + common.trailingWhiteSpace().suppress()
    )
