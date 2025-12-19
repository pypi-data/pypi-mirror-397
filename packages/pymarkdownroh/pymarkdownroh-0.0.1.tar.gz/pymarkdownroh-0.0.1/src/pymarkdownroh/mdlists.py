"""Create markdown list."""

def create_list(items:list, ordered:bool = False, checklist:bool = False, level:int = 0, indent_unit:str = "    "):
    """
    Convert a nested Python structure (list/dict/str/tuple) into a Markdown list or checklist.

    - items: list | dict | str | tuple
      * str → a single item
      * list → sequence of items (str, dict, tuple, nested lists)
      * dict → keys are items, values are sub-items
      * tuple → (item, bool) for checklists (True = checked)
    - ordered: if True, use '1.' for all items (Markdown auto-numbers them).
    - checklist: if True, use [ ] / [x] boxes.
    - level: current nesting level (internal).
    - indent_unit: indentation string per level (default 4 spaces for VS Code/CommonMark).
    """

    # Result list containing all the created markdown strings.
    lines = []
    # Identation level which is normally 2 but 4 on vscode.
    indent = indent_unit * level

    # Internal function to append parent and childitems to the list.
    def add_parent_and_children(parent_line:str, children):
        
        lines.append(parent_line)

        if children is not None:

            lines.append(create_list(children, ordered, checklist, level + 1, indent_unit))

    # Check if item is string.
    if isinstance(items, str):
        # Check if the result should be a checklist and ordered.
        if checklist:
            if ordered:
                # Ordered list start with 1. . Markdown counts the correct number itself.
                lines.append(f"{indent}1. [ ] {items}")
            else:
                lines.append(f"{indent}- [ ] {items}")
        else:
            lines.append(f"{indent}{'1.' if ordered else '-'} {items}")
    
    # Check if items is tuple.
    elif isinstance(items, tuple) and checklist:
        text, checked = items
        mark = "x" if checked else " "

        if ordered:
            lines.append(f"{indent}1. [{mark}] {text}")
        else:
            lines.append(f"{indent}- [{mark}] {text}")
    
    # Check if items is dict.
    elif isinstance(items, dict):
        for key, children in items.items():
            if checklist:
                parent = f"{indent}{'1.' if ordered else '-'} [ ] {key}"
            else:
                parent = f"{indent}{'1.' if ordered else '-'} {key}"
            
            add_parent_and_children(parent, children)
    
    # Check if items is list.
    elif isinstance(items, list):
        for item in items:
            if isinstance(item, str):
                if checklist:
                    if ordered:
                        lines.append(f"{indent}1. [ ] {item}")
                    else:
                        lines.append(f"{indent}- [ ] {item}")
                else:
                    lines.append(f"{indent}{'1.' if ordered else '-'} {item}")

            elif isinstance(item, tuple) and checklist:
                text, checked = item
                mark = "x" if checked else " "
                if ordered:
                    lines.append(f"{indent}1. [{mark}] {text}")
                else:
                    lines.append(f"{indent}- [{mark}] {text}")

            elif isinstance(item, dict):
                for key, children in item.items():
                    if checklist:
                        parent = f"{indent}{'1.' if ordered else '-'} [ ] {key}"
                    else:
                        parent = f"{indent}{'1.' if ordered else '-'} {key}"
                    add_parent_and_children(parent, children)

            else:
                lines.append(create_list(item, ordered, checklist, level, indent_unit))

    return "\n".join(lines)
