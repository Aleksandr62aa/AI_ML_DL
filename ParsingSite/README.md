## Brief description of the program

The program is designed for parsing site packages.
Data is saved in files in “json”, “csv”, “xml” formats.
The operation of the program is shown using the example of parsing packages from the site https://pypi.org/search/?q={}.

## When writing the program used:
1. Asynchronous code (for making HTTP requests and storing data on the hard drive).
2. Design pattern - factory method.
3. Inheritance and composition.
4. Data storage from the site is carried out in the data class and then the data is written to the hard disk.
5. Principles of SOLID.
6. File saving formats “json”, “csv”, “xml”.

## The program is a mini platform for parsing other sites.
To use the program for parsing sites, you must:
- inherit the abstract class "Service(ABC)";
- redefine abstract methods "parse_sit", "output_service".
