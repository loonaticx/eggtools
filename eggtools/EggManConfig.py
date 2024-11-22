import fnmatch
from dataclasses import dataclass, field


@dataclass
class NodeNameConfig:
    """
    NodeNameConfig applies certain attributes to nodes that match a pattern.
    """
    NODE_INCLUDES: set = field(default_factory = lambda: set())

    def check(self, name_pattern):
        # Check if any pattern in NODE_INCLUDES matches the name_pattern as a wildcard
        return any(
            fnmatch.fnmatch(name_pattern, pattern) or fnmatch.fnmatch(pattern, name_pattern)
            for pattern in self.NODE_INCLUDES
        )


# Configurations with patterns supporting wildcards
DualConfig = NodeNameConfig(
    NODE_INCLUDES = {""}
)

DecalConfig = NodeNameConfig(
    NODE_INCLUDES = {"*decal*"}
)

BackstageConfig = NodeNameConfig(
    NODE_INCLUDES = {"bkstg*"}
)

if __name__ == "__main__":
    test_name = "decal"
    test = DecalConfig.check(test_name)
    print(test)
