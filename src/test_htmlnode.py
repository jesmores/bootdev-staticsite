import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

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

class TestParentNode(unittest.TestCase):
	def test_parent_basic(self):
		parent = ParentNode(
			"p",
			[
				LeafNode("b", "Bold"),
				LeafNode(None, " text"),
			]
		)
		self.assertEqual(parent.to_html(), "<p><b>Bold</b> text</p>")

	def test_parent_with_props(self):
		parent = ParentNode(
			"div",
			[LeafNode("span", "x")],
			props={"class": "box", "id": "main"}
		)
		self.assertEqual(parent.to_html(), '<div class="box" id="main"><span>x</span></div>')

	def test_parent_nested(self):
		inner = ParentNode("em", [LeafNode(None, "inner")])
		outer = ParentNode("strong", [LeafNode(None, "pre "), inner, LeafNode(None, " post")])
		self.assertEqual(outer.to_html(), "<strong>pre <em>inner</em> post</strong>")

	def test_parent_raises_no_tag(self):
		with self.assertRaises(ValueError):
			ParentNode("", [LeafNode(None, "x")]).to_html()

	def test_parent_raises_no_children(self):
		with self.assertRaises(ValueError):
			ParentNode("div", []).to_html()

	def test_parent_deeply_nested_four_levels(self):
		# div > section > article > p > span(text)
		leaf = LeafNode("span", "deep")
		p = ParentNode("p", [leaf])
		article = ParentNode("article", [p])
		section = ParentNode("section", [article])
		deep = ParentNode("div", [section])
		expected = "<div><section><article><p><span>deep</span></p></article></section></div>"
		self.assertEqual(deep.to_html(), expected)

	def test_parent_mixed_text_and_elements(self):
		parent = ParentNode(
			"p",
			[
				LeafNode(None, "A "),
				LeafNode("b", "B"),
				LeafNode(None, " C"),
				LeafNode("i", "I"),
			]
		)
		self.assertEqual(parent.to_html(), "<p>A <b>B</b> C<i>I</i></p>")

	def test_parent_inner_parent_with_props(self):
		inner = ParentNode("section", [LeafNode(None, "X")], props={"data-s": "1"})
		outer = ParentNode("div", [inner], props={"id": "root"})
		self.assertEqual(outer.to_html(), '<div id="root"><section data-s="1">X</section></div>')

	def test_parent_props_order_preserved(self):
		props = {"data-b": "2", "data-a": "1", "id": "x"}
		parent = ParentNode("div", [LeafNode(None, "y")], props=props)
		self.assertEqual(parent.to_html(), '<div data-b="2" data-a="1" id="x">y</div>')

if __name__ == "__main__":
	unittest.main()




