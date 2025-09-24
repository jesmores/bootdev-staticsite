import unittest

from parsing import *
from textnode import *


class TestSplitDelimiter(unittest.TestCase):
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

    def test_split_nodes_border(self):
        node = TextNode("**Bold at start** and normal and *italic at end*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("Bold at start", TextType.BOLD),
                TextNode(" and normal and ", TextType.TEXT),
                TextNode("italic at end", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_split_nodes_consecutive_delimiters(self):
        node = TextNode("`CodeBlock``MoreCode` normal text ` end code`` at the border`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("CodeBlock", TextType.CODE),
                TextNode("MoreCode", TextType.CODE),
                TextNode(" normal text ", TextType.TEXT),
                TextNode(" end code", TextType.CODE),
                TextNode(" at the border", TextType.CODE),
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
        self.assertListEqual([], new_nodes)

    def test_split_nodes_delimiter_just_delimiter(self):
        node = TextNode("`code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("code", TextType.CODE),
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


class TestSplitReplaceStringsWithNodes(unittest.TestCase):
    def test_empty_splits_returns_original(self):
        nodes = [TextNode("some text", TextType.TEXT)]
        result = split_replace_strings_with_nodes(nodes, [])
        self.assertListEqual(nodes, result)

    def test_single_replace(self):
        nodes = [TextNode("hello world", TextType.TEXT)]
        splits = [("world", TextNode("jupiter", TextType.BOLD))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("hello ", TextType.TEXT),
                TextNode("jupiter", TextType.BOLD),
            ],
            result,
        )

    def test_multiple_replaces_in_one_node(self):
        nodes = [TextNode("foo bar foo", TextType.TEXT)]
        splits = [("foo", TextNode("baz", TextType.ITALIC))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("baz", TextType.ITALIC),
                TextNode(" bar ", TextType.TEXT),
                TextNode("baz", TextType.ITALIC),
            ],
            result,
        )

    def test_multiple_different_replaces(self):
        nodes = [TextNode("one two three", TextType.TEXT)]
        splits = [
            ("one", TextNode("1", TextType.CODE)),
            ("three", TextNode("3", TextType.CODE)),
        ]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("1", TextType.CODE),
                TextNode(" two ", TextType.TEXT),
                TextNode("3", TextType.CODE),
            ],
            result,
        )

    def test_replace_at_start(self):
        nodes = [TextNode("start middle end", TextType.TEXT)]
        splits = [("start", TextNode("beginning", TextType.BOLD))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("beginning", TextType.BOLD),
                TextNode(" middle end", TextType.TEXT),
            ],
            result,
        )

    def test_replace_at_end(self):
        nodes = [TextNode("start middle end", TextType.TEXT)]
        splits = [("end", TextNode("finish", TextType.BOLD))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("start middle ", TextType.TEXT),
                TextNode("finish", TextType.BOLD),
            ],
            result,
        )

    def test_replace_full_node_text(self):
        nodes = [TextNode("full", TextType.TEXT)]
        splits = [("full", TextNode("complete", TextType.CODE))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("complete", TextType.CODE),
            ],
            result,
        )

    def test_non_text_nodes_are_ignored(self):
        nodes = [
            TextNode("hello", TextType.TEXT),
            TextNode("world", TextType.CODE),
            TextNode("world", TextType.TEXT),
        ]
        splits = [("world", TextNode("everybody", TextType.BOLD))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("hello", TextType.TEXT),
                TextNode("world", TextType.CODE),
                TextNode("everybody", TextType.BOLD),
            ],
            result,
        )

    def test_replace_in_multiple_nodes(self):
        nodes = [
            TextNode("first part", TextType.TEXT),
            TextNode("second part", TextType.TEXT),
        ]
        splits = [("part", TextNode("section", TextType.ITALIC))]
        result = split_replace_strings_with_nodes(nodes, splits)
        self.assertListEqual(
            [
                TextNode("first ", TextType.TEXT),
                TextNode("section", TextType.ITALIC),
                TextNode("second ", TextType.TEXT),
                TextNode("section", TextType.ITALIC),
            ],
            result,
        )

    def test_replace_with_text_node_raises_error(self):
        nodes = [TextNode("hello world", TextType.TEXT)]
        splits = [("world", TextNode("everyone", TextType.TEXT))]
        with self.assertRaises(ValueError):
            split_replace_strings_with_nodes(nodes, splits)


class TestSplitNodesImages(unittest.TestCase):
    def test_single_image_mid_text(self):
        nodes = [TextNode("Hello ![Alt](https://img/a.png) world", TextType.TEXT)]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("Alt", TextType.IMAGE, "https://img/a.png"),
                TextNode(" world", TextType.TEXT),
            ],
            result,
        )

    def test_multiple_images(self):
        nodes = [TextNode("Start ![one](a.png) mid ![two](b.jpg) end", TextType.TEXT)]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("Start ", TextType.TEXT),
                TextNode("one", TextType.IMAGE, "a.png"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("two", TextType.IMAGE, "b.jpg"),
                TextNode(" end", TextType.TEXT),
            ],
            result,
        )

    def test_multiword_alt_text(self):
        nodes = [TextNode("Here is ![an image](img.png) in text", TextType.TEXT)]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("Here is ", TextType.TEXT),
                TextNode("an image", TextType.IMAGE, "img.png"),
                TextNode(" in text", TextType.TEXT),
            ],
            result,
        )

    def test_no_images_returns_same_nodes(self):
        original = [TextNode("No pics here", TextType.TEXT)]
        result = split_nodes_images(original)
        self.assertListEqual(original, result)

    def test_images_at_boundaries(self):
        nodes = [TextNode("![a](a.png) middle ![b](b.png)", TextType.TEXT)]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("a", TextType.IMAGE, "a.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "b.png"),
            ],
            result,
        )

    def test_non_text_nodes_untouched(self):
        nodes = [
            TextNode("prefix ", TextType.TEXT),
            TextNode("code literal ![x](y.png)", TextType.CODE),
            TextNode(" and ![img](z.png) suffix", TextType.TEXT),
        ]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("prefix ", TextType.TEXT),
                TextNode("code literal ![x](y.png)", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "z.png"),
                TextNode(" suffix", TextType.TEXT),
            ],
            result,
        )

    def test_garbled_image_syntax(self):
        nodes = [
            TextNode("This is ![not an image(https://example.com) text", TextType.TEXT),
            TextNode("![also not an image]", TextType.TEXT),
            TextNode("![this is(also not) hello !but t](() ![this one (is)](correct though)!yes", TextType.TEXT)
        ]
        result = split_nodes_images(nodes)
        self.assertListEqual(
            [
                TextNode("This is ![not an image(https://example.com) text", TextType.TEXT),
                TextNode("![also not an image]", TextType.TEXT),
                TextNode("![this is(also not) hello !but t](() ", TextType.TEXT),
                TextNode("this one (is)", TextType.IMAGE, "correct though"),
                TextNode("!yes", TextType.TEXT)
            ],
            result,
        )


class TestSplitNodesLinks(unittest.TestCase):
    def test_single_link_mid_text(self):
        nodes = [TextNode("Hello [site](https://example.com) world", TextType.TEXT)]
        result = split_nodes_links(nodes)
        self.assertListEqual(
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("site", TextType.HYPERLINK, "https://example.com"),
                TextNode(" world", TextType.TEXT),
            ],
            result,
        )

    def test_multiple_links(self):
        nodes = [TextNode("Start [one](a) mid [two](b) end", TextType.TEXT)]
        result = split_nodes_links(nodes)
        self.assertListEqual(
            [
                TextNode("Start ", TextType.TEXT),
                TextNode("one", TextType.HYPERLINK, "a"),
                TextNode(" mid ", TextType.TEXT),
                TextNode("two", TextType.HYPERLINK, "b"),
                TextNode(" end", TextType.TEXT),
            ],
            result,
        )

    def test_no_links_returns_same_nodes(self):
        original = [TextNode("No links here", TextType.TEXT)]
        result = split_nodes_links(original)
        self.assertListEqual(original, result)

    def test_links_at_boundaries(self):
        nodes = [TextNode("[a](a) middle [b](b)", TextType.TEXT)]
        result = split_nodes_links(nodes)
        self.assertListEqual(
            [
                TextNode("a", TextType.HYPERLINK, "a"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("b", TextType.HYPERLINK, "b"),
            ],
            result,
        )

    def test_non_text_nodes_untouched(self):
        nodes = [
            TextNode("prefix ", TextType.TEXT),
            TextNode("code literal [x](y)", TextType.CODE),
            TextNode(" and [one](a) suffix", TextType.TEXT),
        ]
        result = split_nodes_links(nodes)
        self.assertListEqual(
            [
                TextNode("prefix ", TextType.TEXT),
                TextNode("code literal [x](y)", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("one", TextType.HYPERLINK, "a"),
                TextNode(" suffix", TextType.TEXT),
            ],
            result,
        )

    def test_garbled_link_syntax(self):
        nodes = [
            TextNode("This is [not a link(https://example.com) text", TextType.TEXT),
            TextNode("[also (chin) not a link]((asdf()", TextType.TEXT),
            TextNode("[this is(also not) hello !but t](() [this one (is)](correct though)!yes", TextType.TEXT)
        ]
        result = split_nodes_links(nodes)
        self.assertListEqual(
            [
                TextNode("This is [not a link(https://example.com) text", TextType.TEXT),
                TextNode("[also (chin) not a link]((asdf()", TextType.TEXT),
                TextNode("[this is(also not) hello !but t](() ", TextType.TEXT),
                TextNode("this one (is)", TextType.HYPERLINK, "correct though"),
                TextNode("!yes", TextType.TEXT)
            ],
            result,
        )


class TestParseTextToTextNodes(unittest.TestCase):
    def test_plain_text(self):
        text = "Just some plain text."
        result = text_to_textnodes(text)
        self.assertListEqual([TextNode(text, TextType.TEXT)], result)

    def test_composite_case(self):
        text = "This is **bold** and _italic_ and a `code` block with a [link](https://example.com) and an image ![alt](img.png)."
        result = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and a ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" block with a ", TextType.TEXT),
                TextNode("link", TextType.HYPERLINK, "https://example.com"),
                TextNode(" and an image ", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "img.png"),
                TextNode(".", TextType.TEXT),
            ],
            result,
        )

    def test_border_delimiter(self):
        text = "**Bold at start** and normal and _italic at end_"
        result = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Bold at start", TextType.BOLD),
                TextNode(" and normal and ", TextType.TEXT),
                TextNode("italic at end", TextType.ITALIC),
            ],
            result,
        )

    def test_border_image_link(self):
        text = "![img](a.png) middle [link](b.com)"
        result = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "a.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("link", TextType.HYPERLINK, "b.com"),
            ],
            result,
        )

    def test_adjacent_simple_and_image_or_link(self):
        text = "This is **bold**![img](a.png)[link](b.com)_italic_`code`"
        result = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode("img", TextType.IMAGE, "a.png"),
                TextNode("link", TextType.HYPERLINK, "b.com"),
                TextNode("italic", TextType.ITALIC),
                TextNode("code", TextType.CODE),
            ],
            result,
        )

    def test_embedded_delimiters_in_image_or_link(self):
        text = "![**bold alt**](a.png) and [*italic link*](b.com)"
        result = text_to_textnodes(text)
        # note that currently this is not supported so we will ignore simple markdown inside image or link nodes
        self.assertListEqual(
            [
                TextNode("**bold alt**", TextType.IMAGE, "a.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("*italic link*", TextType.HYPERLINK, "b.com"),
            ],
            result,
        )


class TestBlockSplitter(unittest.TestCase):
    def test_single_block(self):
        text = "This is a single block of text."
        result = markdown_to_blocks(text)
        self.assertListEqual([text], result)

    def test_no_text(self):
        text = "\n\n\n"
        result = markdown_to_blocks(text)
        self.assertListEqual([], result)

    def test_multiple_blocks(self):
        text = "First block.\n\nSecond block.\n\nThird block."
        result = markdown_to_blocks(text)
        self.assertListEqual(
            ["First block.", "Second block.", "Third block."], result
        )

    def test_leading_trailing_newlines(self):
        text = "\n\nLeading newlines.\n\nTrailing newlines.\n\n"
        result = markdown_to_blocks(text)
        self.assertListEqual(["Leading newlines.", "Trailing newlines."], result)

    def test_consecutive_newlines(self):
        text = "Block one.\n\n\n\nBlock two after multiple newlines."
        result = markdown_to_blocks(text)
        self.assertListEqual(
            ["Block one.", "Block two after multiple newlines."], result
        )

    def test_blanklines_with_whitespace(self):
        text = "Block one\n  \n\nBlock Two.\n\n\t\n\t\nBlock Three."
        result = markdown_to_blocks(text)
        self.assertListEqual(["Block one", "Block Two.", "Block Three."], result)

    def test_excess_newlines_and_whitespace(self):
        text = "  \t\n\n  Block with leading/trailing spaces.  \n\t\n\n  Another block.  \n  "
        result = markdown_to_blocks(text)
        self.assertListEqual(
            ["Block with leading/trailing spaces.", "Another block."], result
        )

    def test_single_newlines_no_split(self):
        text = "\n\nThis is a block\nwith a single newline.\n\t\t   \nNow this is \na new block.\n"
        result = markdown_to_blocks(text)
        self.assertListEqual(
            ["This is a block\nwith a single newline.", "Now this is \na new block."],
            result
        )

    def test_code_blocks(self):
        text = "Here is some code:\n\n```\ndef foo():\n    return 'bar'\n```\n\nAnd some more text."
        result = markdown_to_blocks(text)
        self.assertListEqual(
            [
                "Here is some code:",
                "```\ndef foo():\n    return 'bar'\n```",
                "And some more text."
            ],
            result
        )

    def test_code_blocks_preserve_newlines(self):
        text = "Here is a cobe block:\n\n```This code block\n\nhas internal blocks\nwith newlines\n\t\nand another block.```\n\nThey should have been preserved."
        result = markdown_to_blocks(text)
        self.assertListEqual(
            [
                "Here is a cobe block:",
                "```This code block\n\nhas internal blocks\nwith newlines\n\t\nand another block.```",
                "They should have been preserved."
            ],
            result
        )

    def test_code_blocks_surrounded_by_whitespace(self):
        text = "Here is a code block:  \t  ```This code block\n\nNew Block\nNew Line\n\nAnother block.```  \n\nEnd Text."
        result = markdown_to_blocks(text)
        self.assertListEqual(
            [
                "Here is a code block:",
                "```This code block\n\nNew Block\nNew Line\n\nAnother block.```",
                "End Text."
            ],
            result
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_block(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_not_heading_too_many_hashes(self):
        self.assertEqual(block_to_block_type("####### Not a heading"), BlockType.PARAGRAPH)

    def test_not_heading_no_space(self):
        self.assertEqual(block_to_block_type("#no-space"), BlockType.PARAGRAPH)

    def test_code_block(self):
        self.assertEqual(block_to_block_type("```code```"), BlockType.CODEBLOCK)
        self.assertEqual(block_to_block_type("```\ncode\nblock\n```"), BlockType.CODEBLOCK)

    def test_quote_block(self):
        self.assertEqual(block_to_block_type("> quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("> quote1\n> quote2"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("> quote1\n\t\t> quote2\n\t> quote3"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">quote with no space\n>another quote with no space\n> quote with space"), BlockType.QUOTE)
        self.assertNotEqual(block_to_block_type("extra text >quote text"), BlockType.QUOTE)

    def test_unordered_list_block(self):
        self.assertEqual(block_to_block_type("- item1"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("- item1\n- item2"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("- item1\n    - item2"), BlockType.UNORDERED_LIST)
        self.assertNotEqual(block_to_block_type("-itemA"), BlockType.UNORDERED_LIST)

    def test_ordered_list_block(self):
        self.assertEqual(block_to_block_type("1. item1\n2. item2"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("1. item1\n3. item2"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("321. item1\n   332. item2"), BlockType.ORDERED_LIST)
        self.assertNotEqual(block_to_block_type("1.itemA"), BlockType.ORDERED_LIST)

    def test_paragraph_block(self):
        self.assertEqual(block_to_block_type("Just a paragraph."), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1) not an ordered list"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("hello >not a quote"), BlockType.PARAGRAPH)


class TestExtractTitle(unittest.TestCase):
    def test_single_level_1_heading(self):
        text = "# This is the Title\n\nSome other text."
        self.assertEqual(extract_title(text), "This is the Title")

    def test_multiple_headings(self):
        text = "# Main Title\n\n## Subtitle\n\nMore text.\n\n# Another Title"
        self.assertEqual(extract_title(text), "Main Title")

    def test_no_level_1_heading(self):
        text = "## Subtitle Only\n\nNo main title here."
        print(f"***********{text}")
        with self.assertRaises(ValueError):
            extract_title(text)

    def test_heading_with_leading_trailing_spaces(self):
        text = "#   Title with Spaces   \n\nContent follows."
        self.assertEqual(extract_title(text), "Title with Spaces")

    def test_heading_with_special_characters(self):
        text = "# Title! @#$$%^&*()_+\n\nBody text."
        self.assertEqual(extract_title(text), "Title! @#$$%^&*()_+")

    def test_empty_heading(self):
        text = "# \n\nNo title text."
        self.assertEqual(extract_title(text), "")

    def test_heading_not_at_start(self):
        text = "Some intro text.\n\n# Actual Title\n\nMore content."
        self.assertEqual(extract_title(text), "Actual Title")

    def test_multiple_level_1_headings_only_first_used(self):
        text = "# First Title\n# Second Title\n# Third Title"
        self.assertEqual(extract_title(text), "First Title")