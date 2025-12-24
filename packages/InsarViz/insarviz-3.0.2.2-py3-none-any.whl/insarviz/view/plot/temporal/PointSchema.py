from .__prelude__ import (
    Qt,
    MapPoint, PointCurve, LinearCurve, SigmoidCurve, PeriodicCurve,
    StructRoles, StructSchema, MaybeStructSchema, FloatSliderSchema,
    BoolSchema
)

class PlotPointRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled | Qt.Qt.ItemFlag.ItemIsEditable | Qt.Qt.ItemFlag.ItemIsUserCheckable
    @staticmethod
    def field_roles(field):
        if field == "color":
            return [Qt.Qt.ItemDataRole.DecorationRole]
        if field == "name":
            return [Qt.Qt.ItemDataRole.DisplayRole]
        if field == "show_in_map":
            return [Qt.Qt.ItemDataRole.CheckStateRole]
        return None
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return model.name
        if role == Qt.Qt.ItemDataRole.DecorationRole:
            return model.color
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            return Qt.Qt.CheckState.Checked if model.show_in_plot else Qt.Qt.CheckState.Unchecked
    @staticmethod
    def set_role(model, role, value):
        if role == Qt.Qt.ItemDataRole.EditRole:
            model.name = value
            return True
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            model.show_in_plot = (value == Qt.Qt.CheckState.Checked.value)
            return True
        return False
class PointCurveRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def field_roles(field):
        if field == "is_empty":
            return [Qt.Qt.ItemDataRole.CheckStateRole]
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Fit Curve"
        if role == Qt.Qt.ItemDataRole.CheckStateRole:
            return Qt.Qt.CheckState.Checked if not model.is_empty else Qt.Qt.CheckState.Unchecked
class SigmoidCurveRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Sigmoid Curve"
class LinearCurveRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Linear Curve"
class SeasonalCurveRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Seasonal Curve"
class SemiSeasonalCurveRoles(StructRoles):
    @staticmethod
    def flags():
        return Qt.Qt.ItemFlag.ItemIsEnabled
    @staticmethod
    def get_role(model, role):
        if role == Qt.Qt.ItemDataRole.DisplayRole:
            return "Semi-Seasonal Curve"

point_curve_schema = StructSchema(
    PointCurve, PointCurveRoles,
    ("linear_curve",
     MaybeStructSchema(
         LinearCurve, LinearCurveRoles)),
    ("sigmoid_curve",
     MaybeStructSchema(
         SigmoidCurve, SigmoidCurveRoles,
         ("initial_step", FloatSliderSchema("Step position", f_min = -1.0, f_max = 1.0)))),
    ("seasonal_curve",
     MaybeStructSchema(
         PeriodicCurve, SeasonalCurveRoles)),
    ("semi_seasonal_curve",
     MaybeStructSchema(
         PeriodicCurve, SemiSeasonalCurveRoles)),
)
point_schema = StructSchema(
    MapPoint, PlotPointRoles,
    ("show_variance", BoolSchema("Standard deviation")),
    ("point_curve",point_curve_schema))
focus_point_schema = StructSchema(
    MapPoint, PlotPointRoles,
    ("show_variance", BoolSchema("Standard deviation")),
    ("point_curve",point_curve_schema),
    ("focus", FloatSliderSchema("Focus"))
)
