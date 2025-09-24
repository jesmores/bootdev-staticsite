import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, convert_newlines_to_spaces, parse_code_block, parse_heading_block, parse_ordered_list_block, parse_quote_block, parse_unordered_list_block, text_node_to_html_node, markdown_to_html_node
from textnode import TextNode, TextType

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

    def test_to_html_allows_empty_value(self):
        node = LeafNode(tag="span", value="")
        self.assertEqual(node.to_html(), "<span></span>")

    def test_to_html_handles_none_value_as_empty(self):
        node = LeafNode(tag="span", value=None)
        self.assertEqual(node.to_html(), "<span></span>")

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

    def test_parent_equality(self):
        p1 = ParentNode("div", [LeafNode("span", "x")], props={"id": "a"})
        p2 = ParentNode("div", [LeafNode("span", "x")], props={"id": "a"})
        p3 = ParentNode("div", [LeafNode("span", "y")], props={"id": "a"})
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)

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


class TestConvertNewlinesToSpaces(unittest.TestCase):
    def test_simple_newline(self):
        text = "This is a line.\nThis is another line."
        expected = "This is a line. This is another line."
        self.assertEqual(convert_newlines_to_spaces(text), expected)

    def test_multiple_newlines(self):
        text = "Line one.\n\nLine two.\n\n\nLine three."
        expected = "Line one. Line two. Line three."
        self.assertEqual(convert_newlines_to_spaces(text), expected)

    def test_leading_line_whitespace(self):
        text = "   Whitespace\n   new line with whites \n \t\n\t     and more spaces.\n"
        expected = "Whitespace new line with whites and more spaces."
        self.assertEqual(convert_newlines_to_spaces(text), expected)


class TestParseHeadingBlock(unittest.TestCase):
    def test_valid_h1_heading(self):
        self.assertEqual(parse_heading_block("# Heading 1"), ParentNode("h1", [LeafNode(None, "Heading 1")]))
        self.assertEqual(parse_heading_block("#   Heading 1   "), ParentNode("h1", [LeafNode(None, "Heading 1")]))
        self.assertEqual(parse_heading_block("# Heading with inner # hash"), ParentNode("h1", [LeafNode(None, "Heading with inner # hash")]))

    def test_h2_heading_with_inlines(self):
        self.assertEqual(
            parse_heading_block("## Heading with **bold** and _italic_ text"),
            ParentNode(
                "h2",
                [
                    LeafNode(None, "Heading with "),
                    LeafNode("b", "bold"),
                    LeafNode(None, " and "),
                    LeafNode("i", "italic"),
                    LeafNode(None, " text"),
                ],
            ),
        )

    def test_heading_partial_lines(self):
        self.assertEqual(
            parse_heading_block("# Heading\nwith partial line\nwhoops"),
            ParentNode("h1", [LeafNode(None, "Heading with partial line whoops")])
        )

    def test_heading_with_inline_at_borders(self):
        self.assertEqual(
            parse_heading_block("### **Bold** at start and _italic_ at end `with code`"),
            ParentNode(
                "h3",
                [
                    LeafNode("b", "Bold"),
                    LeafNode(None, " at start and "),
                    LeafNode("i", "italic"),
                    LeafNode(None, " at end "),
                    LeafNode("code", "with code"),
                ],
            ),
        )

    def test_valid_h6_heading(self):
        self.assertEqual(parse_heading_block("###### Heading 6"), ParentNode("h6", [LeafNode(None, "Heading 6")]))
        self.assertEqual(parse_heading_block("######    Heading 6    "), ParentNode("h6", [LeafNode(None, "Heading 6")]))

    def test_invalid_heading_too_many_hashes(self):
        self.assertRaises(ValueError, parse_heading_block, "####### Too many hashes")

    def test_invalid_heading_no_space(self):
        self.assertRaises(ValueError, parse_heading_block, "##No space")

    def test_not_a_heading(self):
        self.assertRaises(ValueError, parse_heading_block, "Just some text without heading")


class TestParseCodeBlock(unittest.TestCase):
    def test_valid_code_block(self):
        code = """```i am a code block```"""
        expected = ParentNode("pre", children=[LeafNode("code", "i am a code block")])
        self.assertEqual(parse_code_block(code), expected)

    def test_empty_code_block(self):
        code = """``````"""
        expected = ParentNode("pre", children=[LeafNode("code", "")])
        self.assertEqual(parse_code_block(code), expected)

    def test_code_block_preserve_format_codes(self):
        code = """```this is a code block\nwith embedded\n\nnewlines and *markdown*\nit should not process them```"""
        expected = ParentNode("pre", children=[LeafNode("code", "this is a code block\nwith embedded\n\nnewlines and *markdown*\nit should not process them")])
        self.assertEqual(parse_code_block(code), expected)


class TestParseQuoteBlock(unittest.TestCase):
    def test_single_line_quote(self):
        quote = "> This is a quote"
        expected = ParentNode("blockquote", [LeafNode(None, "This is a quote")])
        self.assertEqual(parse_quote_block(quote), expected)

    def test_multiline_quote(self):
        quote = """> This is a quote
> that spans multiple lines
> and should be treated as a single block."""
        expected = ParentNode(
            "blockquote",
            [
                LeafNode(None, "This is a quote\n"),
                LeafNode(None, "that spans multiple lines\n"),
                LeafNode(None, "and should be treated as a single block."),
            ],
        )
        result = parse_quote_block(quote)
        self.assertEqual(result, expected)

    def test_multiline_quote_with_inline_markdown(self):
        quote ="""
> This is a quote with **bold** text
and _italic_ text
> it even has `code` inlines
"""
        expected = ParentNode(
            "blockquote",
            [
                LeafNode(None, "This is a quote with "),
                LeafNode("b", "bold"),
                LeafNode(None, " text and "),
                LeafNode("i", "italic"),
                LeafNode(None, " text\n"),
                LeafNode(None, "it even has "),
                LeafNode("code", "code"),
                LeafNode(None, " inlines"),
            ],
        )
        self.assertEqual(parse_quote_block(quote), expected)


class TestParseUnorderedListBlock(unittest.TestCase):
    def test_single_item_list(self):
        ul = """- Single item"""
        expected = ParentNode("ul", children=[ParentNode("li", children=[LeafNode(None, "Single item")])])
        self.assertEqual(parse_unordered_list_block(ul), expected)

    def test_multiple_item_list(self):
        ul = """- First item
- Second item"""
        expected = ParentNode("ul", children=[
            ParentNode("li", children=[LeafNode(None, "First item")]),
            ParentNode("li", children=[LeafNode(None, "Second item")])
        ])

    def test_multiple_item_list_with_markdown(self):
        ul = """
- First item
- Second item with **bold**
- _Italic_ third item"""
        expected = ParentNode("ul", children=[
            ParentNode("li", children=[LeafNode(None, "First item")]),
            ParentNode("li", children=[LeafNode(None, "Second item with "), LeafNode("b", "bold")]),
            ParentNode("li", children=[LeafNode("i", "Italic"), LeafNode(None, " third item")])
        ])
        self.assertEqual(parse_unordered_list_block(ul), expected)

    def test_list_with_partial_lines(self):
        ul = """- First item
continued line
that `has a code block`
- Second item
has an ![image block](http://example.com)
- Third item
[partial line](http://example.com) starts with a link"""
        expected = ParentNode("ul", children=[
            ParentNode("li", children=[LeafNode(None, "First item continued line that "), LeafNode("code", "has a code block")]),
            ParentNode("li", children=[
                LeafNode(None, "Second item has an "),
                LeafNode("img", None, {"src": "http://example.com", "alt": "image block"})
            ]),
            ParentNode("li", children=[
                LeafNode(None, "Third item "),
                LeafNode("a", "partial line", {"href": "http://example.com"}),
                LeafNode(None, " starts with a link")
            ])
        ])
        result = parse_unordered_list_block(ul)
        self.assertEqual(result, expected)


class TestParseOrderedListBlock(unittest.TestCase):
    def test_single_item_list(self):
        ol = """1. Single item"""
        expected = ParentNode("ol", children=[ParentNode("li", children=[LeafNode(None, "Single item")])])
        self.assertEqual(parse_ordered_list_block(ol), expected)

    def test_multiple_item_list(self):
        ol = """1. First item
2. Second item"""
        expected = ParentNode("ol", children=[
            ParentNode("li", children=[LeafNode(None, "First item")]),
            ParentNode("li", children=[LeafNode(None, "Second item")])
        ])
        self.assertEqual(parse_ordered_list_block(ol), expected)

    def test_multiple_item_list_with_markdown(self):
        ol = """1. First item
2. Second item with **bold**
3. _Italic_ third item"""
        expected = ParentNode("ol", children=[
            ParentNode("li", children=[LeafNode(None, "First item")]),
            ParentNode("li", children=[LeafNode(None, "Second item with "), LeafNode("b", "bold")]),
            ParentNode("li", children=[LeafNode("i", "Italic"), LeafNode(None, " third item")])
        ])
        self.assertEqual(parse_ordered_list_block(ol), expected)

    def test_list_with_embedded_link(self):
        ol = """
1. First item with a [link](http://example.com)
2. [second item](test) starts with a link
"""
        expected = ParentNode("ol", children=[
            ParentNode("li", children=[
                LeafNode(None, "First item with a "),
                LeafNode("a", "link", {"href": "http://example.com"})
            ]),
            ParentNode("li", children=[
                LeafNode("a", "second item", {"href": "test"}),
                LeafNode(None, " starts with a link")
            ])
        ])
        self.assertEqual(parse_ordered_list_block(ol), expected)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_headings(self):
        md_text = """# Heading 1

## Heading 2 _with italic_

### Heading 3 with `code`

#### **Heading 4** begins with a bold character
"""
        html_node = markdown_to_html_node(md_text)
        html_str = html_node.to_html()
        expected_html = "<div><h1>Heading 1</h1><h2>Heading 2 <i>with italic</i></h2><h3>Heading 3 with <code>code</code></h3><h4><b>Heading 4</b> begins with a bold character</h4></div>"
        self.assertEqual(html_str, expected_html)

    def test_codeblocks(self):
        md_text = """# Code Block testing

    ```a code block```

    just some text

```
another code block with
multiple lines

and possibly extra blocks

*oh no* it shouldnt be replacing these **markdown** inside the code block
```

now it's the end and we can go back to **normal text**"""
        html_str = markdown_to_html_node(md_text).to_html()
        expected_html = "<div><h1>Code Block testing</h1><pre><code>a code block</code></pre><p>just some text</p><pre><code>another code block with\nmultiple lines\n\nand possibly extra blocks\n\n*oh no* it shouldnt be replacing these **markdown** inside the code block\n</code></pre><p>now it's the end and we can go back to <b>normal text</b></p></div>"
        self.assertEqual(html_str, expected_html)

    def test_quote_blocks(self):
        md_text = """
# Quote Block test

This is a test for quote blocks.

> here is a quote
> across multiple lines

Ooh a random paragraph

> another quote
with partial lines
> and some _embedded markdown_
"""
        html_str = markdown_to_html_node(md_text).to_html()
        expected_html = "<div><h1>Quote Block test</h1><p>This is a test for quote blocks.</p><blockquote>here is a quote\nacross multiple lines</blockquote><p>Ooh a random paragraph</p><blockquote>another quote with partial lines\nand some <i>embedded markdown</i></blockquote></div>"
        self.assertEqual(html_str, expected_html)

    def test_lists(self):
        md_text = """
# List test

## Unordered list

- First item
- Second item [has a link](test)
- **Bolded third item**

## Ordered list

1. First item
2. ![image](test) Second item starts with an `image`

Done!"""
        self.maxDiff = None
        html_str = markdown_to_html_node(md_text).to_html()
        expected_html = '<div><h1>List test</h1><h2>Unordered list</h2><ul><li>First item</li><li>Second item <a href="test">has a link</a></li><li><b>Bolded third item</b></li></ul><h2>Ordered list</h2><ol><li>First item</li><li><img src="test" alt="image"></img> Second item starts with an <code>image</code></li></ol><p>Done!</p></div>'
        self.assertEqual(html_str, expected_html)

    def test_general(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_general_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )