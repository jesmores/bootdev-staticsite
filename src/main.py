import os
import shutil
import sys

from htmlnode import markdown_to_html_node
from parsing import extract_title


def scratchpad():
    pass


def clear_directory(path:str) -> bool:
    """Given a directory path, clear its contents"""
    # print(f"Clearing directory: {path}")
    if not os.path.exists(path):
        return False

    for path_item in os.listdir(path):
        item_path = os.path.join(path, path_item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            if not clear_directory(item_path):
                return False
            os.rmdir(item_path)

    return True


def copy_directory(src:str, dst:str) -> bool:
    """Copy the contents of one directory to another"""
    # print(f"Copying from {src} to {dst}")
    if not os.path.exists(src):
        return False

    if not os.path.exists(dst):
        os.mkdir(dst)

    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)

        if os.path.isdir(src_item):
            if not copy_directory(src_item, dst_item):
                return False
        else:
            shutil.copy2(src_item, dst_item)

    return True

def prepare_directory(src:str, dst:str) -> bool:
    """Prepare a directory by clearing it and copying new contents"""
    # first make sure src and dst are absolute paths
    if not os.path.isabs(src) or not os.path.isabs(dst):
        raise ValueError("Both src and dst must be absolute paths")

    # next clear and then copy src to dst
    if not clear_directory(dst):
        return False
    if not copy_directory(src, dst):
        return False

    return True


def generate_page(from_path:str, template_path:str, dest_path:str) -> None:
    print (f"Generating page from {from_path}  to {dest_path} using {template_path}")
    # read the source file
    content_md = ""
    with open(from_path, 'r', encoding='utf-8') as f:
        content_md = f.read()
    # read the template file
    template_html = ""
    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()

    title_text = extract_title(content_md)
    content_html = markdown_to_html_node(content_md).to_html()

    title_template_str = "{{ Title }}"
    content_template_str = "{{ Content }}"

    # replace the template strings with the actual content
    output_html = template_html.replace(title_template_str, title_text)
    output_html = output_html.replace(content_template_str, content_html)

    # write output_html to dest_path
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(output_html)


def main():
    # first determine what our script's current directory is
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    # next build the paths we need
    public_dir = os.path.join(base_dir, "public")
    static_dir = os.path.join(base_dir, "static")

    try:
        if not prepare_directory(static_dir, public_dir):
            print("Failed to prepare the public directory")
            sys.exit(1)
    except Exception as e:
        print(f"Error preparing directories: {e}")
        sys.exit(1)

    content_dir = os.path.join(base_dir, "content")
    content_file_path = os.path.join(content_dir, "index.md")
    template_file_path = os.path.join(base_dir, "template.html")
    output_file_path = os.path.join(public_dir, "index.html")
    try:
        generate_page(content_file_path, template_file_path, output_file_path)
    except Exception as e:
        print(f"Error generating page: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "scratch":
        result = scratchpad()
        if result is not None:
            print(result)
    else:
        main()