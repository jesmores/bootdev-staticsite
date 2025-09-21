import unittest

from parsing import *
from textnode import *


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


class TestExtractMarkdownImages(unittest.TestCase):
    def test_single_image(self):
        text = "An image: ![Alt text](https://example.com/img.png)."
        self.assertEqual(
            extract_markdown_images(text),
            [
                (
                    "![Alt text](https://example.com/img.png)",
                    "Alt text",
                    "https://example.com/img.png",
                )
            ],
        )

    def test_multiple_images(self):
        text = "Here is ![one](a.png) and also ![two](b.jpg) in a line."
        self.assertEqual(
            extract_markdown_images(text),
            [
                ("![one](a.png)", "one", "a.png"),
                ("![two](b.jpg)", "two", "b.jpg"),
            ],
        )

    def test_no_images(self):
        text = "There are no images here."
        self.assertEqual(extract_markdown_images(text), [])

    def test_not_link_but_similar(self):
        # Plain links shouldn't be captured by image extractor
        text = "A link [site](https://example.com) but no image."
        self.assertEqual(extract_markdown_images(text), [])
    
    def test_mixed_content_only_images(self):
        text = "Here is ![one](a.png), a link [site](https://example.com), and ![two](b.jpg)."
        self.assertEqual(
            extract_markdown_images(text),
            [
                ("![one](a.png)", "one", "a.png"),
                ("![two](b.jpg)", "two", "b.jpg"),
            ],
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_single_link(self):
        text = "Go to [Example](https://example.com)."
        self.assertEqual(
            extract_markdown_links(text),
            [("[Example](https://example.com)", "Example", "https://example.com")],
        )

    def test_multiple_links(self):
        text = "[One](a) and [Two](b) and [Three](c)."
        self.assertEqual(
            extract_markdown_links(text),
            [
                ("[One](a)", "One", "a"),
                ("[Two](b)", "Two", "b"),
                ("[Three](c)", "Three", "c"),
            ],
        )

    def test_ignores_images(self):
        # Links extractor must ignore images (due to negative lookbehind)
        text = "![Alt](img.png) and [Real Link](https://example.com)"
        self.assertEqual(
            extract_markdown_links(text),
            [("[Real Link](https://example.com)", "Real Link", "https://example.com")],
        )
    
    def test_mixed_content_only_links(self):
        text = "Here is [one](a), an image ![img](b.png), and [two](c)."
        self.assertEqual(
            extract_markdown_links(text),
            [("[one](a)", "one", "a"), ("[two](c)", "two", "c")],
        )

    def test_no_links(self):
        text = "Just text with (parentheses) and [brackets] but not links."
        self.assertEqual(extract_markdown_links(text), [])
