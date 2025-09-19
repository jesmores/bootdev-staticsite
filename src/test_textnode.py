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
