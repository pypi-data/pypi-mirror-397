
"""
Simple HTML String Renderer (Server-Side Rendering)
"""
from .renderer import BaseRenderer

class HTMLRenderer(BaseRenderer):
    def __init__(self):
        self.root = None

    def create_instance(self, type_tag: str, props: dict) -> 'HTMLElement':
        return HTMLElement(type_tag, props)

    def create_text_instance(self, text: str) -> 'HTMLText':
        return HTMLText(text)

    def append_child(self, parent_instance, child_instance):
        # Avoid duplicates - only append if not already a child
        if child_instance not in parent_instance.children:
            parent_instance.children.append(child_instance)

    def remove_child(self, parent_instance, child_instance):
        if child_instance in parent_instance.children:
            parent_instance.children.remove(child_instance)

    def insert_before(self, parent_instance, child_instance, before_instance):
        if before_instance in parent_instance.children:
            idx = parent_instance.children.index(before_instance)
            parent_instance.children.insert(idx, child_instance)
        else:
            self.append_child(parent_instance, child_instance)

    def update_instance_props(self, instance, type_tag, old_props, new_props):
        instance.props = new_props

    def update_text_instance(self, instance, old_text, new_text):
        instance.text = new_text

class HTMLElement:
    def __init__(self, tag, props):
        self.tag = tag
        self.props = props
        self.children = []

    def __str__(self):
        from .events import register_handler
        attrs = []
        
        # Inject Volta ID for interactivity target
        # import uuid
        # self_id = str(uuid.uuid4())
        # attrs.append(f'data-volta-id="{self_id}"')
        
        for k, v in self.props.items():
            if k == "children": continue
            if k == "className": k = "class"
            
            # Handle Events
            if (k.startswith("on") or k.startswith("on_")) and callable(v):
                # Register the handler
                uid = register_handler(v)
                # Map standard 'onClick' -> 'click', 'oninput' -> 'input'
                event_name = k.lower().replace("on_", "").replace("on", "")
                # We attach a special attribute that our client JS will read
                # e.g. onclick="volta.dispatch('uid')"
                # Or simpler: data-on-click="uid"
                attrs.append(f'data-v-on-{event_name}="{uid}"')
                continue
            
            if k == "style" and isinstance(v, dict):
                # Convert dict to css string
                # Convert camelCase keys to kebab-case (e.g. backgroundColor -> background-color)
                def camel_to_kebab(name):
                    import re
                    # Insert hyphen before uppercase letters and convert to lowercase
                    return re.sub(r'([a-z])([A-Z])', r'\1-\2', name).lower()
                
                style_str = "; ".join([f"{camel_to_kebab(sk)}: {sv}" for sk, sv in v.items()])
                attrs.append(f'{k}="{style_str}"')
            else:
                attrs.append(f'{k}="{v}"')
        
        attr_str = " " + " ".join(attrs) if attrs else ""
        
        # Self closing?
        if not self.children and self.tag in ["input", "img", "br", "hr", "meta"]:
             return f"<{self.tag}{attr_str} />"
             
        inner = "".join(str(c) for c in self.children)
        return f"<{self.tag}{attr_str}>{inner}</{self.tag}>"

class HTMLText:
    def __init__(self, text):
        self.text = text
    
    def __str__(self):
        return self.text
