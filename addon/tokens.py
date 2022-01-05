from enum import Enum, auto

class istr:
    text:str = None
    index:int = -1
    
    def __len__(self) -> bool:
        return self.text.__len__()

    def __eq__(self, __o: object) -> bool:
        if(isinstance(__o, istr)):
            return self.text == __o.text
        return False

    def __init__(self, text:str, index:int) -> None:
        self.text = text
        self.index = index

    def __str__(self) -> str:
        return self.text

    def append(self, content:str) -> None:
        self.text += content

class tokenizationState(Enum):
    dataState = auto()
    characterReferenceState = auto()
    tagOpenState = auto()
    RCDataState = auto()
    RCDataLessThanSignState = auto()
    rawTextState = auto()
    scriptDataState = auto()
    plainTextState = auto()
    endTagOpenState = auto()
    tagNameState = auto()
    RCDATAEndTagOpenState = auto()
    RCDATAEndTagNameState = auto()
    rawTextLessThanSignState = auto()
    rawTextEndTagOpenState = auto()
    rawTextEndTagNameState = auto()
    scriptDataLessThanSignState = auto()
    scriptDataEndTagOpenState = auto()
    scriptDataEndTagNameState = auto()
    scriptDataEscapeStartState = auto()
    scriptDataEscapeStartDashState = auto()
    scriptDataEscapedState = auto()
    scriptDataEscapedDashState = auto()
    scriptDataEscapedDashDashState = auto()
    scriptDataEscapedLessThanSignState = auto()
    scriptDataEscapedEndTagOpenState = auto()
    scriptDataEscapedEndTagNameState = auto()
    scriptDataDoubleEscapeStartState = auto()
    scriptDataDoubleEscapedState = auto()
    scriptDataDoubleEscapedDashState = auto()
    scriptDataDoubleEscapedDashDashState = auto()
    scriptDataDoubleEscapedLessThanSignState = auto()
    scriptDataDoubleEscapeEndState = auto()
    beforeAttributeNameState = auto()
    attributeNameState = auto()
    afterAttributeNameState = auto()
    beforeAttributeValueState = auto()
    attributeValueDoubleQuotedState = auto()
    attributeValueSingleQuotedState = auto()
    attributeValueUnquotedState = auto()
    afterAttributValueQuotedState = auto()
    selfClosingStartTagState = auto()
    bogusCommentState = auto()
    markupDeclarationOpenState = auto()
    commentStartState = auto()
    commentStartDashState = auto()
    commentState = auto()
    commentLessThanSignState = auto()
    commentLessThanSignBangState = auto()
    commentLessThanSignBangDashState = auto()
    commentLessThanSignBangDashDashState = auto()
    commentEndDashState = auto()
    commentEndState = auto()
    commentEndBangState = auto()
    doctypeState = auto()
    beforeDoctypeNameState = auto()
    doctypeNameState = auto()
    afterDoctypeNameState = auto()
    afterDoctypePublicKeywordState = auto()
    beforeDoctypePublicIDState = auto()
    doctypePublicIDDoubleQuotedState = auto()
    doctypePublicIDSingleQuotedState = auto()
    afterDoctypePublicIDState = auto()
    betweenDoctypePublicSystemIDsState = auto()
    afterDoctypeSystemKeywordState = auto()
    beforeDoctypeSystemIDState = auto()
    doctypeSystemIDDoubleQuotedState = auto()
    doctypeSystemIDSingleQuotedState = auto()
    afterDoctypeSystemIDState = auto()
    bogusDoctypeState = auto()
    CDATASectionState = auto()
    CDATASectionBracketState = auto()
    CDATASectionEndState = auto()
    namedCharacterReferenceState = auto()
    ambiguousAmpersandState = auto()
    numericCharacterReferenceState = auto()
    hexCharacterReferenceStartState = auto()
    decCharacterReferenceStartState = auto()
    hexCharacterReferenceState = auto()
    decCharacterReferenceState = auto()
    numericCharacterReferenceEndState = auto()

class attribute():
    name:istr = None
    value:istr = None

    def __eq__(self, __o: object) -> bool:
        if(isinstance(__o, attribute)):
            return self.name.text == __o.name.text
        return False

class doctypeToken():
    tagOpen:int = None
    name:istr = None
    publicID:istr = None
    systemID:istr = None
    forceQuirks:bool = False
    tagClose:int = None

class tagToken():
    tagOpen:int = None
    tagName:istr = None
    selfClosing:bool = False
    attributes:list[attribute] = list()
    currentAttribute:attribute = None
    tagClose:int = None
    # canPushCurrentAttribute:bool = None

    def __str__(self) -> str:
        ret:str = ""
        ret += "<" + self.tagName.text
        for attr in self.attributes:
            ret += " " + attr.name.text + " = " + attr.value.text
        ret += ">"
        return ret

    # def checkCurrentAttribute(self) -> bool:
    #     if self.currentAttribute.name in self.attributes:
    #         self.canPushCurrentAttribute = False
    #     else:
    #         self.canPushCurrentAttribute = True
    #     return self.canPushCurrentAttribute

    def newAttribute(self, name:istr, value:istr):
        self.currentAttribute = attribute()
        self.currentAttribute.name = name
        self.currentAttribute.value = value

    def pushCurrentAttribute(self) -> bool:
        for attr in self.attributes:
            if self.currentAttribute.__eq__(attr):
                return False

        self.attributes.append(self.currentAttribute)
        return True


        # if self.canPushCurrentAttribute is None:
        #     print("AnkiIDE ERROR: CanPushCertain attribute is none for tag %s" % (self.__str__()))
        #     return False

        # if self.canPushCurrentAttribute is False:
        #     return False
        # self.canPushCurrentAttribute = None

class startTagToken(tagToken):
    None

class endTagToken(tagToken):
    None

class characterToken():
    char:istr = None

class commentToken():
    data:istr = None

    def append(self, content:str) -> None:
        self.data.text += content
