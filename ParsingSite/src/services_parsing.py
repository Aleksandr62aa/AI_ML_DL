"""
Contains services to perform data fetching and persisting
"""
import os
import json
import csv
from typing import Text
from abc import ABC, abstractmethod
from xml.dom import minidom

import lxml
import aiohttp
import aiofiles
from aiocsv import AsyncWriter
from bs4 import BeautifulSoup as bs
from aiofiles import os as async_os

from data import SiteData


class Service(ABC):

    SITE_URL_FORMAT = "https://pypi.org/search/?q={http}"
    OUTPUT_DIR = "output"

    @abstractmethod
    def parse_site(self, site_data: Text,  
                  keyword: str) -> SiteData | None:
        raise NotImplementedError("parse_sate should be implemented!")

    @abstractmethod  
    async def output_service(self, keyword: str, 
                            site_data: Text) -> None:
        raise NotImplementedError("output_service should be implemented!")

    async def get_site(self, url: str, 
                        http_session: aiohttp.ClientSession) -> Text:
        """
        Request the web-page from the url

        Args:
            @url: str -> where to download site settings
            @http_session: aiohttp.ClientSession -> HTTP session required 
                            to be bypassed to the function

        Returns:
            type: Text -> site data in XML format
        """
        async with http_session.get(url) as resp:

            try:
                
                self.logger.info(f"status HTTP = {resp.status}")
                return bs(await resp.text(), 'lxml')
            
            except aiohttp.ClientError as http_error:
                self.logger.exception(f"Error getting site Pypi by url  \
                                        ({url}) -> { http_error}")
            
            except Exception as error:
                self.logger.exception(f"Error Pypi -> {error}")

    async def task_make(self, http_session: aiohttp.ClientSession, 
                        keyword: str = "http") -> None:
        """
        Creates  tasks web-get and  parsing site
        Args:
            @http_session: aiohttp.ClientSession -> HTTP session
            keyword: str -> parameter URL        
        Returns:
            type: None
        """
        url = self.SITE_URL_FORMAT.format(keyword)
        self.logger.info(url)

        site_data = await self.get_site(url, http_session)

        await self.output_service(keyword, site_data)

class PypiService(Service):
    """
    Service the web-page from the url with Pypi site
    """

    SITE_URL_FORMAT = "https://pypi.org/search/?q={}"
    OUTPUT_DIR = "output"

    def __init__(self, logger, **kwargs) -> None:
        self.logger = logger
        self.kwargs = kwargs

    def parse_site(self, site_data: Text,  
                    keyword: str) -> SiteData | None:
        """
        Parse web-page site from the url
        Args:
            type: Text -> site data in XML format
            keyword: str -> parameter URL

        Returns:
            type: SiteiData -> web page parameters from URL
        """
        soup_all = site_data.findAll("a", class_="package-snippet")
        
        if not soup_all:
            return None

        data_site_dict = {"name": keyword, "packages": []}

        for id, date in enumerate(soup_all):
            if id == 10:
                break
            dict = {}
            dict["name"] = date.find(
                "span", class_="package-snippet__name").text
            dict["version"] = date.find(
                "span", class_="package-snippet__version").text

            dict["date"] = date.find(
                "span", class_="package-snippet__created").text.strip()
            data_site_dict["packages"].append(dict)

        return SiteData.from_dict(data_site_dict)

    async def output_service(self, keyword: str, site_data: Text) -> None:
        """
        Output data web-page site  to hard drive

        Args:
            keyword: str -> parameter URL  
            site_data: Text  -> site data in XML format
        Returns:
            type: None 
        """

        pypidata = self.parse_site(site_data, keyword)

        if not pypidata:
            self.logger.info(f"Package not found")
            return None

        try:
            directory_path = os.path.join(self.OUTPUT_DIR, keyword)
            await FileService.make_directory(directory_path)

            if not os.path.exists(directory_path):
                self.logger.info(f"{directory_path} not make")
                return None

            self.logger.info(f"{directory_path} make")

            for obj in self.kwargs.values():

                file_path = os.path.join(directory_path,
                                         f"{keyword}.{obj.FORMAT}")

                await obj.save_to_file(file_path, pypidata)

                if not os.path.isfile(file_path):
                    self.logger.info(f"{directory_path} not make")
                self.logger.info(f"{file_path} make")

        except OSError as error:
            self.logger.exception(f"Operating system error -> {error}")


class FileService(ABC):
    """
    Service for working with file format
    """

    @abstractmethod
    def format_to_file(sitedata: SiteData) -> SiteData:
        raise NotImplementedError("Format_to_file should be implemented!")

    @abstractmethod
    def creat_file_service() -> "FileService":
        raise NotImplementedError("Creat_file_service should be implemented!")

    @staticmethod
    async def make_directory(directory_path: str) -> None:
        """
        Creates the tree of directories in the file syste if not exists
        Args:
            @directory_path: str -> path to create        
        """
        await async_os.makedirs(directory_path, exist_ok=True)

    async def save_to_file(self, file_path: str, sitedata: SiteData) -> None:
        """
        Save stream data to the file, using chuncks

        Args:
            file_path: str -> where to save the file
            sitedata: SiteData -> web page parameters from URL             
        """

        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(self.format_to_file(sitedata))


class FileServiceJSON(FileService):
    """
    Service for working with file format JSON
    """
    FORMAT = "json"

    @staticmethod
    def format_to_file(sitedata: SiteData) -> json:
        """
        Formatting data sitedata
        """
        return (json.dumps({"packages": sitedata.packages}, indent=4))
    
    @staticmethod
    def creat_file_service() -> "FileServiceJSON":
        """
        Creates  instance type FileService       
        Returns:
            type: FileService -> class instance type FileService
        """
        return FileServiceJSON()        


class FileServiceCSV(FileService):
    """
    Service for working with file format CSV
    """
    FORMAT = "csv"

    @staticmethod
    def format_to_file(sitedata: SiteData) -> csv:
        """
        Formatting data sitedata
        """
        try:
            return ([list(sitedata.packages[0].keys())] +
                    [list(i.values()) for i in sitedata.packages])
        except IndexError as error:
            print("IndexError")

    async def save_to_file(self, file_path: str, sitedata: SiteData) -> None:
        """
        Save stream data to the file, using chuncks

        Args:
            file_path: str -> where to save the file
            sitedata: SiteData -> web page parameters from URL             
        """

        async with aiofiles.open(file_path, mode='w') as file:
            writer = AsyncWriter(file, delimiter=';')
            await writer.writerows(self.format_to_file(sitedata))

    @staticmethod
    def creat_file_service() -> "FileServiceCSV":
        """
        Creates  instance type FileService       
        Returns:
            type: FileService -> class instance type FileService
        """
        return FileServiceCSV()


class FileServiceXML(FileService):
    """
    Service for working with file format XML
    """
    FORMAT = "xml"

    @staticmethod
    def format_to_file(sitedata: SiteData) -> lxml:
        """
        Formatting data sitedata
        """
        root = minidom.Document()
        xml = root.createElement('packages')
        root.appendChild(xml)

        for site_dict in sitedata.packages:

            productChild = root.createElement('package')
            productChild.setAttribute("name", site_dict['name'])
            xml.appendChild(productChild)

            version = root.createElement("version")
            version.appendChild(root.createTextNode(site_dict['version']))
            productChild.appendChild(version)

            date = root.createElement('date')
            date.appendChild(root.createTextNode(site_dict['date']))
            productChild.appendChild(date)

        xml.appendChild(productChild)
        return root.toprettyxml(indent="\t")

    @staticmethod
    def creat_file_service() -> "FileServiceXML":
        """
        Creates  instance type FileService       
        Returns:
            type: FileService -> class instance type FileService
        """
        return FileServiceXML()
  