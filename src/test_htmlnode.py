import unittest

from htmlnode import HTMLNode, LeafNode

class TestHTMLNode(unittest.TestCase):
	def test_init_defaults(self):
		node = HTMLNode()
		self.assertIsNone(node.tag)
		self.assertIsNone(node.value)
		self.assertIsNone(node.children)
		self.assertIsNone(node.props)

	def test_init_custom(self):
		children = [HTMLNode(tag="span", value="child1"), HTMLNode(tag="b", value="child2")]
		props = {"class": "container", "id": "main"}
		node = HTMLNode(tag="div", value=None, children=children, props=props)
		self.assertEqual(node.tag, "div")
		self.assertIsNone(node.value)
		self.assertEqual(node.children, children)
		self.assertEqual(node.props, props)

	def test_props_to_html_none(self):
		node = HTMLNode()
		self.assertEqual(node.props_to_html(), "", "Expected empty string when props is None")

	def test_props_to_html_empty_dict(self):
		node = HTMLNode(props={})
		self.assertEqual(node.props_to_html(), "", "Expected empty string when props is empty dict")

	def test_props_to_html_single(self):
		node = HTMLNode(props={"href": "http://example.com"})
		self.assertEqual(node.props_to_html(), ' href="http://example.com"')

	def test_props_to_html_multiple(self):
		# Order should be preserved as insertion order in dicts (Python 3.7+)
		props = {"class": "btn primary", "data-role": "action", "disabled": "true"}
		node = HTMLNode(props=props)
		expected = ' class="btn primary" data-role="action" disabled="true"'
		self.assertEqual(node.props_to_html(), expected)

	def test_to_html_not_implemented(self):
		node = HTMLNode(tag="p", value="Hello")
		with self.assertRaises(NotImplementedError):
			node.to_html()

	def test_repr(self):
		children = [HTMLNode(tag="em", value="italic"), HTMLNode(tag="strong", value="bold")]
		props = {"class": "text"}
		node = HTMLNode(tag="p", value=None, children=children, props=props)
		rep = repr(node)
		self.assertIn("HTMLNode(tag=p", rep)
		self.assertIn("children=", rep)
		self.assertIn("props={'class': 'text'}", rep)
		# Ensure child representation appears
		self.assertIn("HTMLNode(tag=em", rep)
		self.assertIn("HTMLNode(tag=strong", rep)


class TestLeafNode(unittest.TestCase):
	def test_init_sets_attributes(self):
		node = LeafNode(tag="p", value="Hello")
		self.assertEqual(node.tag, "p")
		self.assertEqual(node.value, "Hello")
		self.assertIsNone(node.children)
		self.assertIsNone(node.props)

	def test_to_html_basic(self):
		node = LeafNode(tag="p", value="Hello")
		self.assertEqual(node.to_html(), "<p>Hello</p>")

	def test_to_html_with_props(self):
		props = {"href": "http://example.com", "target": "_blank"}
		node = LeafNode(tag="a", value="Click", props=props)
		self.assertEqual(node.to_html(), '<a href="http://example.com" target="_blank">Click</a>')

	def test_to_html_raises_when_no_value(self):
		node = LeafNode(tag="span", value="")
		with self.assertRaises(ValueError):
			node.to_html()

	def test_to_html_allows_empty_tag(self):
		node = LeafNode(tag="", value="Hello")
		self.assertEqual(node.to_html(), "Hello")

	def test_to_html_allows_none_tag(self):
		node = LeafNode(tag=None, value="World")
		self.assertEqual(node.to_html(), "World")

	def test_to_html_no_tag_with_props_raises(self):
		node = LeafNode(tag="", value="Hello", props={"class": "c"})
		with self.assertRaises(ValueError):
			node.to_html()

	def test_to_html_none_tag_with_props_raises(self):
		node = LeafNode(tag=None, value="Hello", props={"id": "x"})
		with self.assertRaises(ValueError):
			node.to_html()

	def test_repr_contains_expected_fields(self):
		node = LeafNode(tag="span", value="x", props={"class": "badge"})
		rep = repr(node)
		self.assertIn("LeafNode(tag=span", rep)
		self.assertIn("value=x", rep)
		self.assertIn("children=None", rep)
		self.assertIn("props={'class': 'badge'}", rep)

if __name__ == "__main__":
	unittest.main()

