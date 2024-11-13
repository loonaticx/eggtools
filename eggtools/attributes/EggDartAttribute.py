from eggtools.attributes.EggAttribute import EggAttribute

from eggtools.components.EggEnums import DartType
from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "none": DartType.NoType,
    "structured": DartType.Structured,
    "sync": DartType.Sync,
    "no_sync": DartType.NoSync,
    "no-sync": DartType.NoSync,
    "nosync": DartType.NoSync,
    "default": DartType.Default,
}


def get_dart_type(dart_name: str):
    return name2id.get(dart_name.lower(), None)


class EggDartAttribute(EggAttribute):
    def __init__(self, dart_type, override_dart_type=False):
        self.override_dart_type = override_dart_type
        if type(dart_type) is bool or type(dart_type) is int:
            if dart_type:
                # True/1
                dart_type = "default"
            else:
                # False/0
                dart_type = "none"
        self.dart_type = dart_type
        self.dart_mode = get_dart_type(self.dart_type)
        if self.dart_mode is None:
            raise EggAttributeInvalid(self, self.dart_type)
        super().__init__(entry_type = "Dart", name = "", contents = self.dart_type)

    @staticmethod
    def get_dart_types():
        return name2id

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()):
            # can hit EggTable objects
            if hasattr(egg_node, 'getDartType') and (self.override_dart_type or not egg_node.getDartType()):
                egg_node.setDartType(self.dart_mode)


class EggDart(EggDartAttribute):
    def __init__(self, dart_type, override_dart_type=False):
        super().__init__(dart_type, override_dart_type)
