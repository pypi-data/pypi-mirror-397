# ui_schema.py

def Label(text, id=None, visible=True, style=None):
    return {"type": "label", "text": text, "id": id, "visible": visible, "style": style}



def Combo(id, options, label=None, default=None):
    combo = {"type": "combobox", "id": id, "options": options, "default": default}
    if label:
        return {"type": "container", "layout": "hbox", "children": [
            Label(label), combo
        ]}
    return combo

def Check(id, text, checked=False):
    return {"type": "checkbox", "id": id, "text": text, "checked": checked}

def Toggle(id, text, checked=False, color="#FFB000"):
    """For your AnimatedToggle"""
    return {"type": "toggle", "id": id, "text": text, "checked": checked, "color": color}

def Group(id, title, layout="vbox", children=None):
    if children is None: children = []
    return {"type": "group", "id": id, "title": title, "layout_type": layout, "children": children}

def Separator():
    return {"type": "separator"}



def Slider(id, label, label_id=None, min_val=0, max_val=100, default=0):
    """
    id: The core ID (e.g. 't2_1').
        -> Creates slider 'hs_t2_1'
        -> Creates value label 'lb_t2_1'
    label_id: The ID for the title text (e.g. 'lb_ft2_1').
    """
    return {
        "type": "slider_group",
        "label": label,
        "label_id": label_id, # <--- Added this
        "slider": {"id": id, "min": min_val, "max": max_val, "value": default}
    }


