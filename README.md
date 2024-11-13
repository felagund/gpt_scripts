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

These are the icons:

![alt text](https://github.com/felagund/gpt_scripts/blob/master/Screenshots/alll_icons.png?raw=true)

### Usage ###
```
make_gpx_for_locus.py [-h] [-t TRACKS] [-w WAYPOINTS] [-ls LOCUS_STYLE] [-ic ICON_MAPPING] [-sg SECTION_GROUPS] [-o OUTPUT] [--delete_previous_custom_output]

options:
  -h, --help            show this help message and exit
  -t TRACKS, --tracks TRACKS
                        Input file with all tracks, defaults to "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/Combined Tracks/All Optional and Regular Tracks (SOME_DATE).gpx" placed in the working directory
  -w WAYPOINTS, --waypoints WAYPOINTS
                        Input filder with all waypoints, defaults to "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/Waypoints/" placed in the working directory; it needs to contain the following files: "All Other Waypoints (SOME_DATE).gpx", "Important information (SOME_DATE).gpx" and "Ressuply
                        Locations (SOME_DATE).gpx" (Starting points are not processed)
  -ls LOCUS_STYLE, --locus_style LOCUS_STYLE
                        Input Locus style file, defaults to "locus_style.txt" placed in the working directory
  -ic ICON_MAPPING, --icon_mapping ICON_MAPPING
                        Input file mapping icons to waypoints, defaults to "icons.txt" placed in the working directory
  -sg SECTION_GROUPS, --section_groups SECTION_GROUPS
                        Input section groups, defaults to "section_groups.txt" placed in the working directory
  -o OUTPUT, --output OUTPUT
                        Output directory, defaults to "GPX Files (For Locus Map app)" placed in the working directory; which it creates anew with every run, when different custom output directory is specified, no clearing takes place unless explicitly asked
  --delete_previous_custom_output
                        If custom output directory specified, it will get deleted if this optino is used
```

# connect_tracks.py #

It works on the GPT master KMZ file. It mainly connects the endpoint so there are not gaps between tracks, which should make routing easier and it also looks prettier. It also divides tracks that meet another option variant and are not broken into smaller segments. To rename them with proper km info, you need to run https://github.com/dave/gpt/ afterwards. It expects a `GPT Master.kmz`in the working directory but its location can be also specified.

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

### License ###
GPL 3, for all.
