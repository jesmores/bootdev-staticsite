import re

from textnode import TextNode, TextType
from parsing import BlockType, block_to_block_type, markdown_to_blocks, text_to_textnodes


class HTMLNode:
    def __init__(self, tag:str|None=None, value:str|None=None, children:list['HTMLNode']|None=None, props:dict[str, str]|None=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError("to_html method not implemented yet")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HTMLNode):
            return False
        # Ensure node types match (LeafNode vs ParentNode should not be equal to base or each other)
        if type(self) is not type(other):
            return False
        return (
            self.tag == other.tag
            and self.value == other.value
            and self.props == other.props
            and self.children == other.children
        )

    def props_to_html(self) -> str:
        if not self.props:
            return ""
        return " " + " ".join([f'{key}="{value}"' for key, value in self.props.items()])

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag:str|None, value:str|None, props:dict[str, str]|None=None) -> None:
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self) -> str:
        value = self.value or ""
        if not self.tag:
            if self.props:
                raise ValueError("Leaf nodes without a tag cannot have props")
            return value
        return f"<{self.tag}{self.props_to_html()}>{value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag:str, children:list[HTMLNode], props:dict[str, str]|None=None) -> None:
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Parent nodes must have a tag")
        if not self.children:
            raise ValueError("Parent nodes must have children")
        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"


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


def parse_heading_block(block:str) -> HTMLNode:
    """Parse a heading block and return an HTMLNode."""
    block = block.strip()
    match = re.match(r"^(#{1,6})\s+(.*)$", block)
    if not match:
        raise ValueError(f"Invalid heading block: {block}")
    level = len(match.group(1))
    content = match.group(2)
    text_nodes = text_to_textnodes(content)
    child_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
    return ParentNode(f"h{level}", children=child_nodes)

def parse_code_block(block:str) -> HTMLNode:
    block = block.strip()
    match = re.match(r"^```(.*)```$", block, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Invalid code block: {block}")
    return ParentNode("pre", children=[LeafNode("code", match.group(1))])

def parse_quote_block(block:str) -> HTMLNode:
    block = block.strip()
    # remove the quote markers
    quotelines = [ql.strip() for ql in re.split(r"^\s*>\s*", block, flags=re.MULTILINE) if ql.strip()]
    child_nodes = []
    single_child = len(quotelines) == 1
    for ql in quotelines:
        text_nodes = text_to_textnodes(ql)
        html_nodes = [text_node_to_html_node(tn) for tn in text_nodes]
        if single_child:
            child_nodes.extend(html_nodes)
        else:
            p_wrapper = ParentNode("p", children=[text_node_to_html_node(tn) for tn in text_nodes])
            child_nodes.append(p_wrapper)
    return ParentNode("blockquote", children=child_nodes)

def parse_unordered_list_block(block:str) -> HTMLNode:
    block = block.strip()
    list_items = [li.strip() for li in re.split(r"^\s*-\s+", block, flags=re.MULTILINE) if li.strip()]
    child_nodes = []
    for li in list_items:
        text_nodes = text_to_textnodes(li)
        html_nodes = [text_node_to_html_node(tn) for tn in text_nodes]
        li_wrapper = ParentNode("li", children=html_nodes)
        child_nodes.append(li_wrapper)
    return ParentNode("ul", children=child_nodes)

def parse_ordered_list_block(block:str) -> HTMLNode:
    block = block.strip()
    # this will be pretty similar to unordered list parsing
    # also remember that the numbers don't matter since they are auto-numbered in HTML
    list_items = [li.strip() for li in re.split(r"^\s*\d+\.\s+", block, flags=re.MULTILINE) if li.strip()]
    child_nodes = []
    for li in list_items:
        text_nodes = text_to_textnodes(li)
        html_nodes = [text_node_to_html_node(tn) for tn in text_nodes]
        li_wrapper = ParentNode("li", children=html_nodes)
        child_nodes.append(li_wrapper)
    return ParentNode("ol", children=child_nodes)



def markdown_to_html_node(markdown:str) -> HTMLNode:
    """Convert markdown string to HTMLNode tree."""
    blocks = markdown_to_blocks(markdown)
    child_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.HEADING:
                # Placeholder for heading block handling
                child_nodes.append(parse_heading_block(block))
            case BlockType.CODEBLOCK:
                # Placeholder for code block handling
                child_nodes.append(parse_code_block(block))
            case BlockType.QUOTE:
                # Placeholder for quote block handling
                child_nodes.append(parse_quote_block(block))
            case BlockType.UNORDERED_LIST:
                # Placeholder for unordered list block handling
                child_nodes.append(parse_unordered_list_block(block))
            case BlockType.ORDERED_LIST:
                # Placeholder for ordered list block handling
                child_nodes.append(parse_ordered_list_block(block))
            case BlockType.PARAGRAPH:
                # Placeholder for paragraph block handling
                text_nodes = text_to_textnodes(block)
                para_child_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
                child_nodes.append(ParentNode("p", children=para_child_nodes))
            case _:
                raise ValueError(f"Unhandled BlockType {block_type} for block: {block}")
    root = ParentNode("div", children=child_nodes)
    return root