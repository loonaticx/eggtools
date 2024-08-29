from typing import Any, Optional, Union

from panda3d.core import Filename


class ImageReference:
    """
    This could be the location of an image
    """

    def __init__(self, name: str, filename: Union[str, Filename], aux_data: Optional[Any] = None):
        """
        :param str name: Relative name of the texture, not correlated to its filename
        """
        self.name = name
        if isinstance(filename, str):
            filename = Filename.fromOsSpecific(filename)
        self.filename = filename
        self.aux_data = aux_data

    def getName(self) -> str:
        return self.name

    def getFilename(self) -> Filename:
        return self.filename
