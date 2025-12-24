from ..__prelude__ import *
from ..ItemChooser import ItemChooser
from ..WidgetTree  import Container, Leaf
from ..ComputedProgressBar import ComputedProgressBar
from ..IconLabel import IconLabel
from ..GLWidget import GLWidget
from ..schema import (
    StructRoles, StructSchema, MaybeStructSchema, FloatSliderSchema, BoolSchema,
    SchemaView, ListSchema
)

def BoldLabel(label):
    ret = Qt.QLabel(label)
    ret.setStyleSheet("font-weight: bold; min-height: 20px;")
    return ret
def icon_with_label(icon, label):
    return Container(Qt.QHBoxLayout, (), [
        Leaf(IconLabel, (Qt.QIcon(icon),)),
        (Leaf(BoldLabel, (label,)), {"stretch":1}),
    ])
