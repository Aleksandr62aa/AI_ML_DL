"""
Contains dataclasses to handle data from the web-page site
"""

from dataclasses import dataclass
import inspect


@dataclass
class SiteData:
    """
    Represents data web-page site 
    """
    name: str = None
    packages: dict = None

    @classmethod
    def from_dict(cls, d_data: dict) -> "SiteData":
        """
        Convert dictionary object to dataclass 

        Args:
            d_data: dict -> dictionary with class arguments

        Returns:
            type: PypiData -> class PypiData
        """
        return cls(**{
            k: v for k, v in d_data.items()
            if k in inspect.signature(cls).parameters
        })
