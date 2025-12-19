# About GPT #
See https://www.wikiexplora.com/GPT to know more about the Greater Patagonian Trail.
# Installation #
Simply [download the scripts](https://github.com/felagund/gpt_scripts/releases/), extract them if not on Windows and run them, for example:
```
python3 make_gpx_for_locus.py
```
or using Windows:
```
make_gpx_for_locus*.exe
```

# make_gpx_for_locus.py #

It transforms the general "GPX Files (For Smartphone Apps)" folder in the GPT track files as distributed by Jan Dudeck into GPX files tailored-made for the [Locus Map Android application](https://www.locusmap.app) with custom-styled tracks amd icons. By default, it needs to run in a directory that contains as subdirectory the unzipped track files from Jan Dudeck, but you can specify other filepaths. It uses three files for configuration:
* `icons.txt`
* `locus_style.txt`
* `section_groups.txt`
  
See the files to see how to change them to change appearance of tracks or icons. The zip file with the icons `gpt_icons.zip` needs to be put to `Android/data/menion.android.locus/files/Locus/icons/. This needs to be done from a computer (since Android 11, app directories are not accessible from a phone). More info about custom icons for Locus here: https://docs.locusmap.app/doku.php?id=manual:advanced:customization:icons.

This is what it looks like for GPT37 just south of Villa O'Higgins:
![Locus Map style](https://github.com/felagund/gpt_scripts/blob/master/Screenshots/gpt37.jpg?raw=true)

These are the icons:

![Loucs Map icons](https://github.com/felagund/gpt_scripts/blob/master/Screenshots/alll_icons.png?raw=true)

Meaning of the icons and style legend, as well as tips for setting up Locus Map for the GPT can be found in the next version of the GPT Manual that is forthcoming as of December 2025.

### Usage ###
```
usage: make_gpx_for_locus.py [-h] [-d DIRECTORY] [-t TRACKS] [-w WAYPOINTS] [-ls LOCUS_STYLE] [-ic ICON_MAPPING] [-sg SECTION_GROUPS] [-o OUTPUT] [--delete_previous_custom_output]

options:
  -h, --help            show this help message and exit
  -d, --directory DIRECTORY
                        Sets default folder with tracks and waypoints. It defaults to "GPT Track Files YEAR/GPX Files (For Smartphone Apps)/ placed in the working directory. The folder is assumed to contain folders "Combined Tracks" and "Waypoints".
  -t, --tracks TRACKS   Sets an input file with all the tracks. It defaults to "GPT Track Files YEAR/GPX Files (For Smartphone Apps)/Combined Tracks/All Optional and Regular Tracks (SOME_DATE).gpx" placed in the working directory.
  -w, --waypoints WAYPOINTS
                        Sets the input folder with all the waypoints. It defaults to "GPT Track Files YEAR/GPX Files (For Smartphone Apps)/Waypoints/" placed in the working directory. It must contain the following files: "All Other Waypoints (SOME_DATE).gpx", "Important information
                        (SOME_DATE).gpx", "Ressuply Locations (SOME_DATE).gpx" and "Section Start and End Points (SOME_DATE)".
  -ls, --locus_style LOCUS_STYLE
                        Sets the input Locus style file. It defaults to "locus_style.txt" placed in the working directory.
  -ic, --icon_mapping ICON_MAPPING
                        Sets the input file that maps icons to waypoints. It defaults to "icons.txt" placed in the working directory.
  -sg, --section_groups SECTION_GROUPS
                        Sets input section groups. It defaults to "section_groups.txt" placed in the working directory.
  -o, --output OUTPUT   Sets output directory. It defaults to "GPX Files (For Locus Map app)" placed in the working directory. It creates this directory anew with every run if present and the default is used. When a different custom output directory is specified, it does not get deleted
                        unless specifically instructed (see the next option).
  --delete_previous_custom_output
                        If a custom output directory is specified (see above), it will be first deleted if it previously exists.
```

# connect_tracks.py #

It works on the GPT master KMZ file. For the file to be then usable by [Dave's GPT script](https://github.com/dave/gpt/, the resulting file needs to be opened once in Google Earth and saved. It mainly connects the endpoints so there are no gaps between tracks. This should make routing easier and it also looks prettier. It also divides tracks that meet another option variant and are not broken into smaller segments. To rename them with proper km info, you need to run Dave's script afterwards. It expects a `GPT Master.kmz`in the working directory, but its location can be also specified.

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
# Instructions to build exe files on Windows guest machine in Virtualbox #

1. Install Python in Windows (download from python.org and run executable). 

2. It must be added to PATH (WTF?):

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

[Providers.xml](https://github.com/felagund/gpt_scripts/blob/master/data/providers.xml) and [Strava.xml](https://github.com/felagund/gpt_scripts/blob/master/data/strava.xml) are taken from https://github.com/mjk912/LocusMapTweak/blob/master/providers.xml and https://download.freemap.sk/LocusMap/locus-providers.xml respectively.

