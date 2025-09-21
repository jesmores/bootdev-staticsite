import re
from textnode import *
from htmlnode import *
import copy


def extract_markdown_images(text:str) -> list[str]:
    """Extracts all markdown image URLs from the given text.

    Args:
        text (str): The text to extract image URLs from.

    Returns:
        list[str]: A list of image URLs found in the text.
    """
    mkd_img_pattern = r"(!\[([^\[\]]+?)\]\(([^\(\)]+?)\))"
    return re.findall(mkd_img_pattern, text)


def extract_markdown_links(text:str) -> list[str]:
    """Extracts all markdown link URLs from the given text.

    Args:
        text (str): The text to extract link URLs from.

    Returns:
        list[str]: A list of link URLs found in the text.
    """
    mkd_link_pattern = r"((?<!!)\[([^\[\]]+?)\]\(([^\(\)]+?)\))"
    return re.findall(mkd_link_pattern, text)


def split_nodes_delimiter(old_nodes:list[TextNode], delimiter:str, text_type:TextType) -> list[TextNode]:
    """Splits TextNodes in old_nodes by the given delimiter, inserting new TextNodes of the given text_type for the delimiters.

    Args:
        old_nodes (list[TextNode]): A list of textnodes to process
        delimiter (str): A delimter character to split on
        text_type (TextType): The TextType for nodes marked by the delimiter

    Returns:
        list[TextNode]: A new list of TextNodes where nodes have been split by the delimiter and new nodes of the given text_type inserted.
    """
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            parts = node.text.split(delimiter)
            # if parts is even length that means there was an unmatched delimiter
            if len(parts) % 2 == 0:
                raise ValueError(f"Found unmatched delimiter '{delimiter}' in text: {node.text}")
            for i, part in enumerate(parts):
                # empty parts usually show up when there are consecutive delimiters or at the start/end of the string
                # don't bother adding empty text nodes
                if not part:
                    continue
                # even indexed parts are outside the delimiters
                if i % 2 == 0:
                    new_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    new_nodes.append(TextNode(part, text_type))
    return new_nodes

def split_replace_strings_with_nodes(old_nodes:list[TextNode], splits:list[tuple[str, TextNode]]) -> list[TextNode]:
    """Given a list of textnodes, match on the given string list and replace the matches with given textnodes"""
    # if there is nothing to split, just return the original list
    if not splits:
        return old_nodes
    
    new_nodes = copy.deepcopy(old_nodes)
    for match, new_node in splits:
        if new_node.text_type == TextType.TEXT:
            raise ValueError("Text replacement nodes are not allowed, otherwise infinite replacements are possible.")
        inter_nodes = []
        for node in new_nodes:
            if node.text_type != TextType.TEXT:
                inter_nodes.append(node)
                continue
            parts = node.text.split(match)
            for i, part in enumerate(parts):
                if part:
                    inter_nodes.append(TextNode(part, TextType.TEXT))
                # add the new node in between the split parts
                if i < len(parts) - 1:
                    inter_nodes.append(copy.deepcopy(new_node))
        new_nodes = inter_nodes
    return new_nodes


def split_nodes_images(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        # dont run parsing on non-text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        image_matches = extract_markdown_images(node.text)
        # if no image matches, just keep the original node
        if not image_matches:
            new_nodes.append(node)
            continue

        # otherwise process the image matches and create nodes for the image matches
        replacements = [(match[0], TextNode(match[1], TextType.IMAGE, match[2])) for match in image_matches]
        new_nodes.extend(split_replace_strings_with_nodes([node], replacements))
    return new_nodes


def split_nodes_links(old_nodes:list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        # dont run parsing on non-text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        link_matches = extract_markdown_links(node.text)
        # if no link matches, just keep the original node
        if not link_matches:
            new_nodes.append(node)
            continue
        
        # otherwise process the link matches and create nodes for the link matches
        replacements = [(match[0], TextNode(match[1], TextType.HYPERLINK, match[2])) for match in link_matches]
        new_nodes.extend(split_replace_strings_with_nodes([node], replacements))
    return new_nodes


def text_to_textnodes(text:str) -> list[TextNode]:
    """Converts a plain text string to a list of TextNodes, parsing for markdown syntax.

    Args:
        text (str): The input text to parse.
    Returns:
        list[TextNode]: A list of TextNodes representing the parsed text.
    """
    nodes = [TextNode(text, TextType.TEXT)]
    # order of these matters, since they are applied sequentially
    nodes = split_nodes_images(nodes)
    nodes = split_nodes_links(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes


def markdown_to_blocks(md_text:str) -> list[str]:
    """Splits markdown text into blocks that were delimited by double newlines"""
    return [block.strip() for block in re.split(r"\n\s*\n", md_text) if block.strip()]