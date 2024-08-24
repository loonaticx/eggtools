from panda3d.core import DSearchPath, Filename
from panda3d.egg import EggData

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eggtools.components import EggContext


class EggDataContext(EggData):
    """
    Intended to try and synchronise any significant modifications done to the EggData to match a respective EggContext
    """
    _egg_filename = Filename()

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

    # accessibility
    @property
    def filename(self):
        return self.egg_filename

    @filename.setter
    def filename(self, filename: Filename):
        self.egg_filename = filename

    def __init__(self, *args, **kwargs):
        super().__init__(EggData(*args, **kwargs))
        # Currently dont know a good reason why you should pass context in kwargs with how EggMan handles them.
        self.context: EggContext | None = kwargs.get("context")

    def read(self, *args, **kwargs):
        super().read(*args, **kwargs)
        self.egg_filename = super().getEggFilename()


    def resolveEggFilename(self, egg_filename: Filename, searchpath: DSearchPath) -> bool:
        # [Potentially] modifies the superclass egg_filename property, let's ensure we are still in sync
        resolved = super().resolveEggFilename(egg_filename, searchpath)
        if resolved:
            self.egg_filename = super().getEggFilename()
        return resolved

    def getEggFilename(self):
        return self.egg_filename

    def setEggFilename(self, egg_filename: Filename) -> bool:
        # Handles the call back to the superclass
        self.egg_filename = egg_filename


    def merge(self, other:EggData):
        # In the future i can do checks to see if this and other context is identical
        # If not (and if both objects have an existing context), then we can run an EggContext method to compare/merge
        if other.context and not self.context:
            self.context = other.context
        super().merge(other)
