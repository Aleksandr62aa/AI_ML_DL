"""
Entry point to the asynchronous site parsing program Pypi
"""
import aiohttp
import asyncio

from services_parsing import PypiService, FileServiceJSON, \
                             FileServiceCSV, FileServiceXML
from logger import LogService


async def main() -> None:
    """
Eentry point of program
    Returns:
        type : None
    """

    async with aiohttp.ClientSession() as session:
        await pypi_service.task_make(session, keyword)


if __name__ == "__main__":

    pypi_service = PypiService(
                    LogService().get_logger(),
                    json=FileServiceJSON.creat_file_service(),
                    csv=FileServiceCSV.creat_file_service(),
                    xml= FileServiceXML.creat_file_service()
    )

    while True:
        keyword = input(
                "Please Requesting data,please [q to quit]:")
        if keyword == 'q':
            break
        asyncio.run(main())
