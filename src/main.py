from textnode import *
from htmlnode import *


def scratchpad():
    """Fill me in to try scenarios manually. Print or return something to see output when run from CLI."""
    node = ParentNode(
        "p",
        [
            LeafNode("b", "Bold Text"),
            LeafNode(None, "Normal Text"),
            LeafNode("i", "Italic Text", props={"class": "italic"}),
            LeafNode(None, " More Normal Text")
        ]
    )
    return node.to_html()


def main():
    pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "scratch":
        result = scratchpad()
        if result is not None:
            print(result)
    else:
        main()