from panda3d.core import DSearchPath, Filename
from panda3d.egg import EggData

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from eggtools.components import EggContext


class EggDataContext(EggData):
    """
    When working with EggMan, EggDataContext should be used over EggData.
    It is a wrapper around EggData with some additional features to keep in sync with the corresponding EggContext.
    """
    _egg_filename = Filename()

    """
    It's important that the filename for the superclass, this class, and the corresponding EggContext class
    to be synchronized with each other.
    """

    @property
    def egg_filename(self) -> Filename:
        return self._egg_filename

    @egg_filename.setter
    def egg_filename(self, filename: Filename):
        if filename and not isinstance(filename, Filename):
            filename = Filename.fromOsSpecific(filename)
        self._egg_filename = filename
        # Redundant call for resolveEggFilename but it's okay
        super().setEggFilename(self._egg_filename)

        # Set context filename if we were called from some other method
        if self.context and (self.context.filename is not filename):
            self.context.filename = filename

    """
    Shortcut properties for conventional reasons
    """
    @property
    def filename(self) -> Filename:
        return self.egg_filename

    @filename.setter
    def filename(self, filename: Filename):
        self.egg_filename = filename

    def __init__(self, *args, **kwargs):
        super().__init__(EggData(*args, **kwargs))
        # Currently dont know a good reason why you should pass context in kwargs with how EggMan handles them.
        self.context: Optional[EggContext] = kwargs.get("context")

    def read(self, *args, **kwargs):
        super().read(*args, **kwargs)
        self.egg_filename = super().getEggFilename()

    def resolveEggFilename(self, egg_filename: Filename, searchpath: DSearchPath) -> bool:
        # [Potentially] modifies the superclass egg_filename property, let's ensure we are still in sync
        resolved = super().resolveEggFilename(egg_filename, searchpath)
        if resolved:
            self.egg_filename = super().getEggFilename()
        return resolved

    def getEggFilename(self) -> Filename:
        return self.egg_filename

    def setEggFilename(self, egg_filename: Filename) -> bool:
        # Handles the call back to the superclass
        self.egg_filename = egg_filename

    def merge(self, other) -> None:
        """
        :param EggDataContext other: Should be EggDataContext and NOT EggData

        Appends the other egg structure to the end of this one.
        The other egg structure is invalidated.
        """
        # In the future i can do checks to see if this and other context is identical
        # If not (and if both objects have an existing context), then we can run an EggContext method to compare/merge
        if other.context and not self.context:
            self.context = other.context
        super().merge(other)
