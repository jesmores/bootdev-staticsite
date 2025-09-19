class HTMLNode:
    def __init__(self, tag:str|None=None, value:str|None=None, children:list['HTMLNode']|None=None, props:dict[str, str]|None=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError("to_html method not implemented yet")
    
    def props_to_html(self) -> str:
        if not self.props:
            return ""
        return " " + " ".join([f'{key}="{value}"' for key, value in self.props.items()])
    
    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag:str|None, value:str|None, props:dict[str, str]|None=None) -> None:
        super().__init__(tag=tag, value=value, children=None, props=props)
    
    def to_html(self) -> str:
        value = self.value or ""
        if not self.tag:
            if self.props:
                raise ValueError("Leaf nodes without a tag cannot have props")
            return value
        return f"<{self.tag}{self.props_to_html()}>{value}</{self.tag}>"
    
class ParentNode(HTMLNode):
    def __init__(self, tag:str, children:list[HTMLNode], props:dict[str, str]|None=None) -> None:
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Parent nodes must have a tag")
        if not self.children:
            raise ValueError("Parent nodes must have children")
        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"