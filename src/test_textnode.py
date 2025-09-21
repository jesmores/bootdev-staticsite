import unittest

from textnode import *

class TestTextNode(unittest.TestCase):
    def test_textnode_equality_simple(self):
        node1 = TextNode("Hello")
        node2 = TextNode("Hello")        
        self.assertEqual(node1, node2, "TextNodes with same text should be equal")

        node3 = TextNode("World")
        self.assertNotEqual(node1, node3, "TextNodes with different text should not be equal")
    
    def test_textnode_equality_types(self):
        node1 = TextNode("Hello", TextType.BOLD)
        node2 = TextNode("Hello", TextType.BOLD)
        self.assertEqual(node1, node2, "TextNodes with same text and type should be equal")

        node3 = TextNode("Hello", TextType.ITALIC)
        self.assertNotEqual(node1, node3, "TextNodes with different types should not be equal")

    def test_textnode_equality_url(self):
        node1 = TextNode("Link", TextType.HYPERLINK, url="http://example.com")
        node2 = TextNode("Link", TextType.HYPERLINK, url="http://example.com")        
        self.assertEqual(node1, node2, "TextNodes with same URL should be equal")

        node3 = TextNode("Link", TextType.HYPERLINK, url="http://different.com")
        self.assertNotEqual(node1, node3, "TextNodes with different URLs should not be equal")

        node4 = TextNode("Link", TextType.HYPERLINK) # No URL
        self.assertNotEqual(node1, node4, "TextNodes with url defined and not defined should not be equal")

        node5 = TextNode("Link", TextType.HYPERLINK) # Also no URL
        self.assertEqual(node4, node5, "TextNodes with no URL should be equal")

    def test_textnode_equality_mixurl(self):
        node1 = TextNode("Image", TextType.IMAGE, url="http://image.com/img.png")
        node2 = TextNode("Image", TextType.HYPERLINK, url="http://image.com/img.png")
        self.assertNotEqual(node1, node2, "TextNodes with different types should not be equal")
        
    def test_textnode_equality_non_textnode(self):
        node = TextNode("Hello")
        self.assertNotEqual(node, "Hello", "TextNode should not be equal to a non-TextNode instance")

    def test_textnode_repr_basic(self):
        node = TextNode("Hello")
        # Default type is TEXT and url is None
        self.assertEqual(repr(node), "TextNode(Hello, text, None)")

    def test_textnode_repr_with_url(self):
        node = TextNode("Link", TextType.HYPERLINK, url="http://example.com")
        self.assertEqual(repr(node), "TextNode(Link, hyperlink, http://example.com)")

    def test_textnode_repr_image_no_url(self):
        node = TextNode("Image", TextType.IMAGE)
        self.assertEqual(repr(node), "TextNode(Image, image, None)")


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_converts_text_type(self):
        text_node = TextNode("Just some text", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "Just some text")

    def test_converts_bold_type(self):
        text_node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_converts_italic_type(self):
        text_node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_converts_code_type(self):
        text_node = TextNode("`code`", TextType.CODE)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "`code`")

    def test_converts_hyperlink_type(self):
        url = "https://www.boot.dev"
        text_node = TextNode("Boot.dev", TextType.HYPERLINK, url)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Boot.dev")
        self.assertEqual(html_node.props, {"href": url})

    def test_converts_image_type(self):
        url = "https://example.com/image.png"
        alt_text = "An example image"
        text_node = TextNode(alt_text, TextType.IMAGE, url)
        html_node = text_node_to_html_node(text_node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, None)
        self.assertEqual(html_node.props, {"src": url, "alt": alt_text})

    def test_hyperlink_raises_if_no_url(self):
        text_node = TextNode("Link without URL", TextType.HYPERLINK)
        with self.assertRaisesRegex(ValueError, "Hyperlink TextNode must have a URL"):
            text_node_to_html_node(text_node)

    def test_image_raises_if_no_url(self):
        text_node = TextNode("Image without URL", TextType.IMAGE)
        with self.assertRaisesRegex(ValueError, "Image TextNode must have a URL"):
            text_node_to_html_node(text_node)
