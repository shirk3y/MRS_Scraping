pdftocsv.py is the command line tool to take the symposium PDF's and extract out the abstract discussion session blocks.

To run the command line utility, you must PDF Miner https://euske.github.io/pdfminer/ installed and can be done via their setup.py.

The command line tools is executed as follows:
python pdftocsv.py

positional arguments:
pdf_dir directory containing pdf abstract files
output_file output file name (MRS.csv?)
url url pdf files came from (http://www.mrs.org/...
is_fall TRUE or FALSE
year_override If your data fails on year, it is not parsable. Pass in here