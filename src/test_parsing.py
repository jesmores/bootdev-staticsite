import unittest

from parsing import split_nodes_delimiter
from textnode import TextNode, TextType


class TestParsing(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        node = TextNode("This is text with a `code` block", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" block", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_multi_word(self):
        node = TextNode("This is text with a **bold phrase** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold phrase", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is text with an *italic* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_multiple_delimiters(self):
        node = TextNode(
            "This is **bold** and *italic* and a `code` block", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and a ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" block", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_delimiter_unmatched_delimiter(self):
        node = TextNode("This is text with an *unmatched delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "*", TextType.ITALIC)

    def test_split_nodes_delimiter_no_text_nodes(self):
        node = TextNode("This is an image", TextType.IMAGE)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual([node], new_nodes)

    def test_split_nodes_delimiter_empty_text(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual([TextNode("", TextType.TEXT)], new_nodes)

    def test_split_nodes_delimiter_just_delimiter(self):
        node = TextNode("`code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode("", TextType.TEXT),
            ],
            new_nodes,
        )
   


if __name__ == "__main__":
    unittest.main()
