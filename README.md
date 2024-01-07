# GeoScrub OSM Repair

GeoScrub OSM Repair is a Python command line tool designed to identify and fix duplicate way warnings in OpenStreetMap (OSM) files. This tool is built to streamline the process of identifying duplicate ways, recording them, exporting the duplicates to a shapefile, and then removing the duplication from the original OSM files.

## Features
- Identifies and resolves duplicate way warnings in OSM files.
- Exports identified duplicate ways to a shapefile.
- Provides a cleaned and repaired OSM file as output.

## Requirements
- Python 3.10
- Dependencies listed in the `requirements.txt` file

## Usage
1. Ensure the required dependencies are installed by running:
   ```bash
   pip install -r requirements.txt
Run the application using the following command:

`python main.py`

You can drag and drop a single OSM file or a directory containing multiple OSM files into the terminal for processing.
The tool will process the input OSM file(s), repair duplicate ways, and generate outputs in the input directory.

## Future
Actively working to enhance GeoScrub OSM Repair by adding more functionality to identify and repair various potential issues in OSM files. I encourage the community to provide suggestions, report issues, and consider contributing to make this tool more robust and versatile. Together, we can improve the tool's capabilities and make it a valuable asset for the OSM community.

## Contribution
If you'd like to contribute, please follow the [contribution guidelines](CONTRIBUTING.md). Your input and collaboration are highly appreciated.

#### Contributors:
- [GISJohn](https://github.com/GISJohnECS)
- [DMich9](https://github.com/dmich9) 

## License
This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the tool according to the terms of the license.
