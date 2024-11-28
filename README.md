# About GPT #
See https://www.wikiexplora.com/GPT to know more about Greater Patagonian Trail.
# Installation #
Simply download the scripts and run them, for example:
```
python3 make_gpx_for_locus.p
```

# make_gpx_for_locus.py #

It transforms the general GPT track files for Smartphones into map with custom-styled tracks amd icons for Locus Map Android application. By default, it needs to run in a directory that contains as subdirectory the unzipped track files from Jan Dudeck, but you can specify other filepaths. It needs three files for configuration:
* `icons.txt`
* `locus_style.txt`
* `section_groups.txt`
  
See the files to see how to change them to change appearance. The zip files with the icons `gpt_icons.zip` needs to be put  to `Android/data/menion.android.locus/files/Locus/icons/. This needs to be done from a computer (since Android 11, app directories are not accessible from a phone). More info about custom icons for Locus here: https://docs.locusmap.app/doku.php?id=manual:advanced:customization:icons.

This is what it looks like for GPT37 just south of Villa O'Higgins:
![Locus Map style](https://github.com/felagund/gpt_scripts/blob/master/Screenshots/gpt37.jpg?raw=true)

These are the icons:

![Loucs Map icons](https://github.com/felagund/gpt_scripts/blob/master/Screenshots/alll_icons.png?raw=true)

Meaning of the icons and style legend, as well as tips for setting up Locus Map for the GPT can be found in the GPT Manual that is forthcoming as of November 2024.

### Usage ###
```
make_gpx_for_locus.py [-h] [-d DIRECTORY] [-t TRACKS] [-w WAYPOINTS] [-ls LOCUS_STYLE] [-ic ICON_MAPPING] [-sg SECTION_GROUPS] [-o OUTPUT]
                             [--delete_previous_custom_output]

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Default folder with tracks and waypoints, defaults to "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/ placed in
                        the working directory. The folder is assumed to contain folders "Combined Tracks" and "Waypoints".
  -t TRACKS, --tracks TRACKS
                        Input file with all tracks, defaults to "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/Combined Tracks/All
                        Optional and Regular Tracks (SOME_DATE).gpx" placed in the working directory
  -w WAYPOINTS, --waypoints WAYPOINTS
                        Input filder with all waypoints, defaults to "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/Waypoints/" placed in
                        the working directory; it needs to contain the following files: "All Other Waypoints (SOME_DATE).gpx", "Important information
                        (SOME_DATE).gpx" and "Ressuply Locations (SOME_DATE).gpx" (Starting points are not processed)
  -ls LOCUS_STYLE, --locus_style LOCUS_STYLE
                        Input Locus style file, defaults to "locus_style.txt" placed in the working directory
  -ic ICON_MAPPING, --icon_mapping ICON_MAPPING
                        Input file mapping icons to waypoints, defaults to "icons.txt" placed in the working directory
  -sg SECTION_GROUPS, --section_groups SECTION_GROUPS
                        Input section groups, defaults to "section_groups.txt" placed in the working directory
  -o OUTPUT, --output OUTPUT
                        Output directory, defaults to "GPX Files (For Locus Map app)" placed in the working directory; which it creates anew with every
                        run, when different custom output directory is specified, no clearing takes place unless explicitly asked
  --delete_previous_custom_output
                        If custom output directory specified, it will get deleted if this option is used

```

# connect_tracks.py #

It works on the GPT master KMZ file. For the file to be then usable by GPT.exe, the resulting file needs to be opened once in Google Earth and saved. It mainly connects the endpoint so there are not gaps between tracks, which should make routing easier and it also looks prettier. It also divides tracks that meet another option variant and are not broken into smaller segments. To rename them with proper km info, you need to run https://github.com/dave/gpt/ afterwards. It expects a `GPT Master.kmz`in the working directory but its location can be also specified.

### Usage
```
usage: connect_tracks.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [--debug] [-sst] [-s1] [-s2] [-l1 FIRST_PASS_LIMIT] [-l2 SECOND_PASS_LIMIT]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        Input KMZ file, defaults to "GPT Master (anynumber).kmz" and if such KMZ file is not found, to any KMZ file in the working directory
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output KMZ file, defaults to "INPUT_FILE_connected_endpoints.kmz"
  --debug               If set, prints out debug files
  -sst, --skip_splitting_tracks
                        If set, breaks a track when endpoint of another track is the middle the first track, only works when first step not skipped
  -s1, --skip_first     If set, skips the first pass
  -s2, --skip_second    If set, skips the second pass
  -l1 FIRST_PASS_LIMIT, --first_pass_limit FIRST_PASS_LIMIT
                        Sets maximum distance under which consecutive points will be moved in first pass (default 35 m) (for nonconsecutive endpoints 75 percent of the value is used, for midpoints, second pass limit is used
  -l2 SECOND_PASS_LIMIT, --second_pass_limit SECOND_PASS_LIMIT
                        Sets maximum distance under which points will be moved in second pass (default 10 m)
```
# Build on Windows guest machine in Virtualbox #

1. Install python in windows (download from python.org and run executable). 

2. It must be added to PATH (WTF):

    a. look for "system variable" in start menu

    b. add the _directory_ to path and move it up (for 3.13, it was:

         i. `C:\Users\virtual\AppData\Local\Programs\Python\Python313\`

         ii. `C:\Users\virtual\AppData\Local\Programs\Python\Python313\Scripts\` (reboot needed, WTF)

4. Working in directory on the Desktop, not sure how to get to the directory shared from my host machine.

5. install dependencies:
`pip install geopy lxml`

4. run:
   
    a. `pyinstaller --onefile make_gpx_for_locus.py`
   
    b. `pyinstaller --onefile --hidden-import=lxml,geopy oconnect_tracks.py`

6. move the exe file from the dist directory

# License #
GPL 3, for all.
