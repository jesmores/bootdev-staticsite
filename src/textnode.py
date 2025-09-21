from enum import Enum
from htmlnode import HTMLNode, LeafNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    HYPERLINK = "hyperlink"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type=TextType.TEXT, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url  # Used for hyperlinks and images
    
    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (self.text == other.text and 
                self.text_type == other.text_type and 
                self.url == other.url)
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node:TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.HYPERLINK:
            if text_node.url is None:
                raise ValueError("Hyperlink TextNode must have a URL")
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            if text_node.url is None:
                raise ValueError("Image TextNode must have a URL")
            return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
        # cant really unittest for this so exclude from coverage
        case _: # pragma: no cover
            raise ValueError(f"Unhandled TextType: {text_node.text_type}")