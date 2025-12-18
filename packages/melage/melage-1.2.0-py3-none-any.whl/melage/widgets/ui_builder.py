# ui_builder.py
from PyQt5 import QtWidgets, QtCore, QtGui
from qtwidgets import AnimatedToggle  # Import your custom toggle


class UIBuilder:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.widgets = {}

    def build(self, schema, layout, context=None):
        """
        Args:
            schema: List of UI definitions.
            layout: The layout to add widgets to.
            context: The object (usually 'self') to attach variables to.
                     This fixes the AttributeError.
        """
        row = 0

        for item in schema:
            widget = None

            # --- 1. NESTED GROUPS & CONTAINERS (Recursive Step) ---
            if item['type'] in ['group', 'container']:
                # Create the container widget
                if item['type'] == 'group':
                    # Visible GroupBox with Title
                    container = QtWidgets.QGroupBox(item['title'])
                    if item.get('id') and context: setattr(context, item['id'], container)
                else:
                    # Invisible Container (QWidget)
                    container = QtWidgets.QWidget()

                # Create the Layout for this container
                if item['layout_type'] == 'hbox':
                    container_layout = QtWidgets.QHBoxLayout(container)
                else:
                    container_layout = QtWidgets.QVBoxLayout(container)

                # Remove margins for cleaner nesting (optional)
                container_layout.setContentsMargins(5, 5, 5, 5)

                # *** RECURSION *** # Build the children into this new layout
                self.build(item['children'], container_layout, context)

                # Add the finished container to the parent
                layout.addWidget(container)
                continue

            # --- 2. RADIO BUTTONS ---
            elif item['type'] == 'radio':
                widget = QtWidgets.QRadioButton(item['text'])
                widget.setChecked(item['checked'])

                if item.get('id') and context:
                    setattr(context, item['id'], widget)
                    # For radio buttons, we often want strict saving/loading
                    widget.setObjectName(item['id'])

                layout.addWidget(widget)

            # --- Separator ---
            if item['type'] == 'separator':
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Sunken)
                line.setStyleSheet("background-color: rgb(50,50,50)")
                layout.addWidget(line)#, row, 0, 1, 1)
                row += 1
                continue

            # --- Label ---
            elif item['type'] == 'label':
                widget = QtWidgets.QLabel(item['text'])
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
                widget.setSizePolicy(sizePolicy)
                if item.get('style'): widget.setStyleSheet(item['style'])

                layout.addWidget(widget)#, row, 0, 1, 1)

                # Assign to self (Fixes 'has no attribute lb_ft2_1')
                if item.get('id') and context:
                    setattr(context, item['id'], widget)

                row += 1

            # --- Slider Group (Title + Value + Slider) ---
            elif item['type'] == 'slider_group':
                # 1. Title Label
                lbl_title = QtWidgets.QLabel(item['label'])
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
                lbl_title.setSizePolicy(sizePolicy)
                layout.addWidget(lbl_title)#, row, 0, 1, 1)

                # Assign Title Label ID (e.g., lb_ft2_1)
                if item.get('label_id') and context:
                    setattr(context, item['label_id'], lbl_title)
                row += 1

                # 2. Value Label
                val = item['slider'].get('value', 0)
                lbl_val = QtWidgets.QLabel(str(val))
                lbl_val.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(lbl_val)#, row, 0, 1, 1)

                # Assign Value Label ID (e.g., lb_t2_1)
                # We assume standard naming "lb_" + slider_id if not provided
                slider_id = item['slider'].get('id')
                val_lbl_id = f"lb_{slider_id}" if slider_id else None

                if val_lbl_id and context:
                    setattr(context, val_lbl_id, lbl_val)

                row += 1

                # 3. Slider
                slider_data = item['slider']
                slider = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
                slider.setRange(slider_data['min'], slider_data['max'])
                slider.setValue(val)
                slider.setObjectName(slider_id)  # Important for getAttributeWidget

                # Connect signal
                slider.valueChanged.connect(lbl_val.setNum)

                layout.addWidget(slider)#, row, 0, 1, 1)

                # Assign Slider ID (e.g., hs_t2_1)
                # We assume standard naming "hs_" + slider_id if not provided
                slider_var_name = f"{slider_id}" if slider_id else None

                if slider_var_name and context:
                    setattr(context, slider_var_name, slider)

                row += 1


            # --- Combobox ---
            elif item['type'] == 'combobox':
                widget = QtWidgets.QComboBox()
                widget.addItems(item['options'])
                cbstyle = """
                    QComboBox QAbstractItemView {border: 1px solid grey; background: white; selection-background-color: #03211c;} 
                    QComboBox {background: #03211c; margin-right: 1px;}
                    QComboBox::drop-down {subcontrol-origin: margin;}
                """
                widget.setStyleSheet(cbstyle)
                layout.addWidget(widget)#, row, 0, 1, 1)

                if item.get('id') and context:
                    setattr(context, item['id'], widget)
                row += 1

            # --- Toggle / Checkbox ---
            elif item['type'] in ['toggle', 'checkbox']:
                if item['type'] == 'toggle':
                    widget = AnimatedToggle(checked_color=item.get('color', "#FFB000"))
                else:
                    widget = QtWidgets.QCheckBox(item['text'])

                widget.setChecked(item['checked'])
                layout.addWidget(widget)#, row, 0, 1, 1)

                if item.get('id') and context:
                    setattr(context, item['id'], widget)
                row += 1

        return self.widgets