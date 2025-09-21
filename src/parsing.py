import re
from textnode import *
from htmlnode import *


def extract_markdown_images(text:str) -> list[str]:
    """Extracts all markdown image URLs from the given text.

    Args:
        text (str): The text to extract image URLs from.

    Returns:
        list[str]: A list of image URLs found in the text.
    """
    mkd_img_pattern = r"(!\[(.+?)\]\((.+?)\))"
    return re.findall(mkd_img_pattern, text)


def extract_markdown_links(text:str) -> list[str]:
    """Extracts all markdown link URLs from the given text.

    Args:
        text (str): The text to extract link URLs from.

    Returns:
        list[str]: A list of link URLs found in the text.
    """
    mkd_link_pattern = r"((?<!!)\[(.+?)\]\((.+?)\))"
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
                # even indexed parts are outside the delimiters
                if i % 2 == 0:
                    new_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    new_nodes.append(TextNode(part, text_type))
    return new_nodes

    
