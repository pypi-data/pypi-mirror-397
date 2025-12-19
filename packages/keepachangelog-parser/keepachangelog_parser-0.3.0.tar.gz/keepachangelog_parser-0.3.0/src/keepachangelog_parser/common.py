from pyparsing import LineEnd, Literal, Suppress, Word, ZeroOrMore, nums, printables

h1 = Literal("# ")
h2 = Literal("## ")
h3 = Literal("### ")

openB = Literal("[")
closeB = Literal("]")
openAB = Literal("<")
closeAB = Literal(">")
openP = Literal("(")
closeP = Literal(")")

maybeLineEndings = ZeroOrMore(LineEnd()).suppress()

trailingWhiteSpace = ZeroOrMore(Word(" \t"))

word = Word(printables, excludeChars="-\n")


def SemVer():
    integer = Word(nums).setParseAction(lambda t: int(t[0]))  # Convert to integer
    dot = Suppress(".")

    major = integer("major")
    minor = integer("minor")
    patch = integer("patch")

    sem_ver = major + dot + minor + dot + patch
    return sem_ver
