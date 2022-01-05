from enum import Enum, auto

# TODO: Implement parse errors
class parseError(Enum):
    unexpectedNullCharacter = auto()
    unexpectedQuestionMarkInsteadOfTagName = auto()
    invalidFirstCharacterofTagName = auto()
    missingEndTagName = auto()
    unexpectedEqualsSignBeforeAttributeName = auto()
    unexpectedCharacterInAttributeName = auto()
    unexpectedCharacterInAttributeValue = auto()
    duplicateAttribute = auto()
    missingAttributeValue = auto()
    missingWhiteSpaceBetweenAttributes = auto()
    unexpectedSolidusInTag = auto()
    cdataInHTMLContent = auto()
    incorrectlyOpenedComment = auto()
    incorrectlyClosedComment = auto()
    abruptClosingOfEmptyComment = auto()
    nestedComment = auto()
    missingWhitespaceBeforeDoctypeName = auto()
    missingDoctypeName = auto()
    invalidCharacterSequenceAfterDoctypeName = auto()
    missingWhitespaceAfterDoctypePublicKeyword = auto()
    missingDoctypePublicIdentifier = auto()
    missingQuoteBeforeDoctypePublicIdentifier = auto()
    abruptDoctypePublicIdentifier = auto()
    missingWhitespaceBetweenDoctypePublicAndSystemIds = auto()
    missingQuoteBeforeDoctypeSystemIdentifier = auto()
    missingWhitespaceAfterDoctypeSystemKeyword = auto()
    missingDoctypeSystemId = auto()
    abruptDoctypeSystemId = auto()
    unexpectedCharacterAfterDoctypeSystemId = auto()
    missingSemicolonAfterCharacterReference = auto()
    unknownNamedCharacterReference = auto()
    absenceOfDigitsInNumericCharacterReference = auto()
    nullCharacterReference = auto()
    characterReferenceOutsideUnicodeRange = auto()
    surrogateCharacterReference = auto()
    noncharactercharacterReference = auto()
    controlCharacterReference = auto()