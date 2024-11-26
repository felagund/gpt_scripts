#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# on windows, build with pyinstaller --one-file connect_tracks.py

#from IPython import embed
from lxml import etree
import io
import os
import copy
import re
from collections import Counter
from collections import namedtuple
from decimal import Decimal
import argparse
import sys
from pathlib import Path
import shutil

WaypointTuple = namedtuple('WaypointTupe', ['name','section','waypoint_xml'])


def pp(element, **kwargs):
     xml = etree.tostring(element, pretty_print=True, **kwargs)
     print(xml.decode(), end='')

def make_root():
    return etree.fromstring('<gpx version="0"></gpx>')

def count_pois(pois_file):
    pois = []
    for poi in pois_file:
        pois.append(poi.find("name").text.split("{")[0].strip())
    print(Counter(pois).most_common())
    return Counter(pois).most_common()

def get_section(name):
    if "{" not in name:
        print("Does not have section: " + name)
        return list(name)
    start = name.find("{") + 1
    end = name.find("}")
    s = name[start:end].split("-")[0]
    # resupply and important imformation waypoints can be assigned to multiple sections with {02, 03}
    sections_list = []
    for x in s.split(","):
        x = x.strip()
        # Some sections are divided into north- and south-bound like 22N and 22s or 29PN and 29PS, disregard
        x = x.strip("S")
        x = x.strip("N")
        sections_list.append(x)
    return sections_list 

def get_groups(section_groups_filename):
    group_lines = open_config_file(
    section_groups_filename,
    "Missing or wrong group specification text file, run script with --help to see how to specify it. Exiting now.")
    groups = []
    for group in group_lines:
        letter = group[0]
        rang = re.findall('GPT(..)', group)
        # three xml files are for all tracks, all waypints and hiking tracks only respectively
        groups.append((int(rang[0]),int(rang[1]),group,make_root(),make_root(),make_root(),letter))
    return groups

def open_file(filename,error_message):
    try:
        with open(filename, "r") as file:
            yield file
    except IOError as error:
        print(error_message)
        sys.exit()

def open_config_file(filename,error_message):
    try:
        with open(filename, "r") as file:
            file_text = file.read()
    except IOError as error:
        print(error_message)
        sys.exit()
    lines = []
    for line in file_text.split("\n"):
        if not line: 
            pass
        elif line.lstrip()[0] == "#":
            pass
        else:
            lines.append(line)
    return lines 

def is_hiking_only(code):
    if ("RR-" in code) or ("OH-" in code):
        return True
    else:
        return False

def gpx_2_str(gpx):
        return etree.tostring(gpx, encoding=str)

def make_style(code,filename):
    style_lines = open_config_file(filename,"Missing or wrong Locus style text file, run script with --help to see how to specify it. Exiting now.")
    style_dict = {}
    for line in style_lines:
        split = line.split("=")
        style_dict[split[0]]=split[1]
    regular_packraft_width = style_dict["regular_packraft_width"]
    regular_width = style_dict["regular_width"]
    optional_packraft_width = style_dict["optional_packraft_width"]
    optional_width = style_dict["optional_width"]
    pr_color = style_dict["pr_color"]
    mr_color = style_dict["mr_color"]
    tl_color = style_dict["tl_color"]
    cc_color = style_dict["cc_color"]
    bb_color = style_dict["bb_color"]
    fy_color = style_dict["fy_color"]
    water_color = style_dict["water_color"]
    out_color = style_dict["out_color"]
    exp_color = style_dict["exp_color"]
    symbol_mix = style_dict["symbol_mix"]
    symbol_exp = style_dict["symbol_exp"]
    symbol_one_way = style_dict["symbol_one_way"]
    symbol_one_way_exp = style_dict["symbol_one_way_exp"]
    width, first_color,second_color,symbol,outline_color,one_way = "","","","","",""
    trail_first = ""
    trail_second = ""

    if "RR" in code:
        width = regular_width
    elif "RH" in code:
        width = regular_width
    elif "RP" in code:
        width = regular_packraft_width
    elif "OP" in code:
        width = optional_packraft_width
    elif "OH" in code:
        width = optional_width
    else:
        print("Style is not regular or optional hiking or packrafting: ",code) 
    if ("RP" in code) or ("OP" in code):
        outline_color = out_color
    if "EXP" in code:
        if code[-1] == "1":
            one_way = symbol_one_way_exp
        else:
            symbol = symbol_exp
        trail = code.split("-")[2]
    else:
        if code[-1] == "1":
            one_way = symbol_one_way
        trail = code.split("-")[1]
        if len(trail) > 2:
            symbol = symbol_mix
    if len(trail) == 2:
        if trail == "PR":
            first_color = pr_color
        elif trail == "MR":
            first_color = mr_color
        elif trail == "TL":
            first_color = tl_color
        elif trail == "CC":
            first_color = cc_color
        elif trail == "BB":
            first_color = bb_color
        elif trail == "FY":
            first_color = fy_color
        elif trail == "LK":
            first_color = water_color
        elif trail == "RI":
            first_color = water_color
        elif trail == "FJ":
            first_color = water_color
        else:
            print("Unkwnown trail code: " + trail)
    else:
        if "EXP" in code:
            trail_first = trail.split("&")[0]
            trail_second = trail.split("&")[1]
        else:
            # For the dashes, the secondary colour is dominant, so for example for TL&CC, CC color is first, as th effect s long dash mostly overlapping the line, thus TL is the second colour (of the effect), so most of the trail is actual the colour of trail
            trail_second = trail.split("&")[0]
            trail_first = trail.split("&")[1]
        if trail_first == "PR":
            first_color = pr_color
        elif trail_first == "MR":
            first_color = mr_color
        elif trail_first == "TL":
            first_color = tl_color
        elif trail_first == "CC":
            first_color = cc_color
        elif trail_first == "BB":
            first_color = bb_color
        elif trail_first == "FY":
            first_color = fy_color
        elif trail_first == "LK":
            first_color = water_color
        elif trail_first == "RI":
            first_color = water_color
        elif trail_first == "FJ":
            first_color = water_color
        else:
            print("Unknown first trail code when making styles: " + trail_first)
        if trail_second == "PR":
            second_color = pr_color
        elif trail_second == "MR":
            second_color = mr_color
        elif trail_second == "TL":
            second_color = tl_color
        elif trail_second == "CC":
            second_color = cc_color
        elif trail_second == "BB":
            second_color = bb_color
        elif trail_second == "FY":
            second_color = fy_color
        elif trail_second == "LK":
            second_color = water_color
        elif trail_second == "RI":
            second_color = water_color
        elif trail_second == "FJ":
            second_color = water_color
        else:
            print("Unkwnown second trail code when making styles: " + trail_second)
    if "EXP" in code:
        second_color = exp_color
    style="""
<extensions>
<line xmlns="http://www.topografix.com/GPX/gpx_style/0/2" xmlns:locus="http://www.locusmap.eu">
    <extensions>
"""
    if width:
        style += """        <locus:lsWidth>""" + width + """</locus:lsWidth>
"""
    if first_color:
        style += """        <locus:lsColorBase>""" + first_color + """</locus:lsColorBase>
"""
    if second_color:
        style += """        <locus:lsColorSymbol>""" + second_color + """</locus:lsColorSymbol>
"""
    if one_way:
        style += """        <locus:lsSymbol>""" + one_way + """</locus:lsSymbol>
"""
    elif symbol:
        style += """        <locus:lsSymbol>""" + symbol + """</locus:lsSymbol>
"""
    if outline_color:
        style += """        <locus:lsColorOutline>""" + outline_color + """</locus:lsColorOutline>
"""
    style += """        <locus:lsUnits>PIXELS</locus:lsUnits>
    </extensions>
</line>
</extensions>
"""
    return style

#arguments on the command line

default_folder = "GPT Track Files YEAR/GPX Files (For Smartphones and Basecamp)/"
parser = argparse.ArgumentParser()
parser.add_argument("-d","--directory",
help='Default folder with tracks and waypoints, defaults to "' + default_folder + ' placed in the working directory. The folder is assumed to contain folders "Combined Tracks" and "Waypoints".')
parser.add_argument("-t","--tracks",
help='Input file with all tracks, defaults to "' + default_folder + 'Combined Tracks/All Optional and Regular Tracks (SOME_DATE).gpx" placed in the working directory')

parser.add_argument("-w","--waypoints",
        help='Input filder with all waypoints, defaults to "' + default_folder + 'Waypoints/" placed in the working directory; it needs to contain the following files: "All Other Waypoints (SOME_DATE).gpx", "Important information (SOME_DATE).gpx" and "Ressuply Locations (SOME_DATE).gpx" (Starting points are not processed)')

parser.add_argument("-ls","--locus_style",
help='Input Locus style file, defaults to "locus_style.txt" placed in the working directory',
default='locus_style.txt')

parser.add_argument("-ic", "--icon_mapping",
help='Input file mapping icons to waypoints, defaults to "icons.txt" placed in the working directory',
default='icons.txt')

parser.add_argument("-sg","--section_groups",
help='Input section groups, defaults to "section_groups.txt" placed in the working directory',
default='section_groups.txt')

parser.add_argument("-o","--output",
help='Output directory, defaults to "GPX Files (For Locus Map app)" placed in the working directory; which it creates anew with every run, when different custom output directory is specified, no clearing takes place unless explicitly asked',
default='GPX Files (For Locus Map app)')

parser.add_argument("--delete_previous_custom_output",
help='If custom output directory specified, it will get deleted if this option is used',
action="store_true")

args = parser.parse_args()

print("Parsing input files")
# Get default filename to read if not specified via command line
if args.tracks:
    tracks_filename = args.tracks
else:
    if args.directory:
        data_source_folder = Path(args.directory)
    else:
        d = next(Path(".").glob("GPT Track Files *"))
        data_source_folder = d / "GPX Files (For Smartphones and Basecamp)/"
    tracks_source_folder = data_source_folder / "Combined Tracks"
    tracks_source_filename = next(tracks_source_folder.glob("All Optional and Regular Tracks*.gpx"))
# Get waypoint folder to read if not specified via command line
if args.waypoints:
    waypoint_folder = args.waypoints
else:
    waypoints_source_folder = data_source_folder / "Waypoints"

#Finds datetamp and checks it is a number
s = str(tracks_source_filename)
datestamp = s[s.rfind("(")+1:s.rfind(")")]
try:
    int(datestamp)
except ValueError:
    print("Input track filename does not have datestamp")
    datestamp = ""

# Open tracks file
print("Reading and processing tracks")
all_tracks_file = open_file(tracks_source_filename,"Missing or wrong all-track file, run script with --help to see how to specify it. Exiting now.")
all_tracks = etree.parse(next(all_tracks_file)).getroot()
hiking_only_tracks = make_root()
sections_hiking_only = {}
# Parse the file, add style, make copies by section and groups
styles_for_codes = {}
sections = {}
groups = get_groups(args.section_groups)
for track in all_tracks:
    code = track[0].text.split(" ")[0]
    if code not in styles_for_codes.keys():
        styles_for_codes[code] = make_style(code,args.locus_style)
    track.insert(2,etree.fromstring(styles_for_codes[code]))
    section = get_section(track[0].text)[0]
    if section not in sections.keys():
        sections[section] = make_root()
        if "P" not in section:
            sections_hiking_only[section] = make_root()
    sections[section].insert(0,copy.deepcopy(track))
    if is_hiking_only(code):
        hiking_only_tracks.append(copy.deepcopy(track))
        # Some hiking tracks are confusingly in packrafting sections only
        try:
            sections_hiking_only[section].append(copy.deepcopy(track))
        except KeyError:
            sections_hiking_only[section] = make_root()
            sections_hiking_only[section].append(copy.deepcopy(track))
            #print(track[0].text, " is marked as hiking only but is in packrafting section")
    num = int(section[:2])
    for group in groups:
        if num in range(group[0],group[1]+1):
            group[3].insert(0,copy.deepcopy(track))
            if is_hiking_only(code):
                group[5].insert(0,copy.deepcopy(track))


print("Reading and processing waypoints")
# Read icon mapping
icons = open_config_file(args.icon_mapping,    
"Missing or wrong file mapping icons to waypoints, run script with --help to see how to specify it. Exiting now.")
icon_mapping = {}
style_string = """<extensions xmlns:locus="http://www.locusmap.eu">
        <locus:icon>file:gpt_icons.zip:XXX.png</locus:icon>
	</extensions>"""
for icon in icons:
    if icon.lstrip()[0] == "#":
        pass
    else:
        line = icon.strip("\n").split(";")
        icon_mapping[line[0]]=style_string.replace("XXX",line[1])

# Open waypoints files
waypoint_files =[]
for x in "All Other Waypoints","Important Inf??mation","Resupply Locations":
    try:
        filename = next(waypoints_source_folder.glob(x + "*.gpx"))
    except StopIteration:
        print("Missing or wrong " + x + " file, run script with --help to see how to specify it. Exiting now.")
        sys.exit()
    file = open_file(filename,"This should not happen, we already tested if file exists.")
    waypoint_files.append(etree.parse(next(file)).getroot())

weirdoes = []
pariahs = []
more_wpts_in_one = []
points = []

# Process all other waypoint file
for wp in waypoint_files[0]:
    name = wp.find("name").text.split("{")[0].strip()
    section = get_section(wp.find("name").text)
    if not "," in name:
        points.append(WaypointTuple(name,section,copy.deepcopy(wp)))

    # Treat waypoints that mark multiple points of interestes (divided by comma in front of {) 
    else:
        # create new waypoint for each unique point of interests (so "water, camp, ford" will become three waypoints "water", "camp", "ford")
        for index,w_tup in enumerate([WaypointTuple(subname.strip(),section,copy.deepcopy(wp)) for subname in name.split(",")]):
            w = w_tup.waypoint_xml
            # move the new waypoint by about 15 m to the East
            w.attrib["lon"] = str(Decimal(w.attrib["lon"]) - (index * Decimal("0.0002")))
            name = w.find("name").text
            # new name has only one point of interest in it
            new_name = w_tup.name + " " + name[name.index("{"):]
            w.find("name").text = new_name
            points.append(w_tup)

#For important and ressuply imformation, we ignore comma in names
o = True
for wp in waypoint_files[1]:
    wp.find("name").text = "Important: " + wp.find("name").text
    points.append(WaypointTuple("Important",get_section(wp.find("name").text),wp))
for wp in waypoint_files[2]:
    wp.find("name").text = "Resupply: " + wp.find("name").text
    points.append(WaypointTuple("Supply Point",get_section(wp.find("name").text),wp))

# apply Locus styling to waypoints
sections_poi = {}
new_w = make_root()
for wp_tup in points:
    wp = wp_tup.waypoint_xml
    section = wp_tup.section
    if wp_tup.name in icon_mapping.keys():
        wp.append(etree.fromstring(icon_mapping[wp_tup.name]))
    else:
        # Prints waypoints that are not styled because they have uncommon name
        weirdoes.append(wp_tup)
        print("This point does not have styling:", wp.find("name").text)
    new_w.append(copy.deepcopy(wp))
    # Sort into sections and groups
    # Typically only runs once apart for some important and resuply information, which can belong to multiple sections
    for s in section:
        if s not in sections_poi.keys():
            sections_poi[s] = make_root()
        sections_poi[s].append(copy.deepcopy(wp))
        try:
            num = int(s[:2])
        except:
            # Waypoints that do not include section data, this should not happen
            print("No section, not including in per section and group files: ")
            pp(wp)
            num = 0
            pariahs.append(copy.deepcopy(wp))
            break
        for group in groups:
            if num in range(group[0],group[1]+1):
                # when point belongs to for example section {03, 04}, include it only once
                # tostring conversion only happens when point belongs to more sections,
                # so performance penalty should be low
                if len(section) == 1  or not(etree.tostring(wp) == etree.tostring(group[4][0])):
                    group[4].insert(0,copy.deepcopy(wp))

print("Writing output:")
print("    Creating output directory")
# Only delete output dir when specified, otherwise only delete when default is used
output_dir = Path(args.output)
if args.delete_previous_custom_output:
    if os.path.exists(output_dir):
         shutil.rmtree(output_dir)
if output_dir == Path("GPX Files (For Locus Map app)"):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
# Make output directory
try:
    os.mkdir(output_dir)
except FileExistsError:
    print("You specified an existing custom directory: " + output_dir +".\n Exiting.")
    sys.exit()

print("    Writing combined files")
combined_folder = output_dir / "Combined Tracks and Waypoints"
tracks_output_filename = combined_folder / ("All hiking and packrafting tracks (" + datestamp + ").gpx")
hiking_only_tracks_output_filename = combined_folder / ("All hiking tracks (" + datestamp + ").gpx")
waypoints_output_filename = combined_folder / ("All waypoints (" + datestamp + ").gpx")
os.makedirs(combined_folder)
tracks_output_filename.write_text(gpx_2_str(all_tracks))
hiking_only_tracks_output_filename.write_text(gpx_2_str(hiking_only_tracks))
waypoints_output_filename.write_text(gpx_2_str(new_w))

print("    Writing files by section")
section_track_folder = output_dir / "Tracks by Section - Both Packrafting and Hiking/"
section_hiking_only_track_folder = output_dir / "Tracks by Section - Only Hiking/"
section_waypoint_folder = output_dir / "Waypoints by Section/"
os.makedirs(section_track_folder)
os.makedirs(section_hiking_only_track_folder)
os.makedirs(section_waypoint_folder)
for section in sections.keys():
    section_track_output_filename = section_track_folder / (section + ".gpx")
    section_track_output_filename.write_text(gpx_2_str(sections[section]))
for section in sections_hiking_only.keys():
    section_hiking_only_track_output_filename = section_hiking_only_track_folder / (section + ".gpx")
    section_hiking_only_track_output_filename.write_text(gpx_2_str(sections_hiking_only[section]))

for section in sections_poi.keys():
    section_waypoint_output_filename = section_waypoint_folder / (section + ".gpx")
    section_waypoint_output_filename.write_text(gpx_2_str(sections_poi[section]))
        
print("    Writing files by group")
group_track_folder = output_dir / "Tracks by Group - Both Packrafting and Hiking/"
group_hiking_only_track_folder = output_dir / "Tracks by Group - Only Hiking/"
group_waypoint_folder = output_dir / "Waypoints by Group/"
os.makedirs(group_track_folder)
os.makedirs(group_waypoint_folder)
os.makedirs(group_hiking_only_track_folder)
for group in groups:
    group_track_output_filename = group_track_folder / (group[2] + ".gpx")
    group_waypoint_output_filename = group_waypoint_folder / (group[2] + ".gpx")
    if len(group[5]) > 1:
        group_hiking_only_track_output_filename = group_hiking_only_track_folder / (group[2] + ".gpx")
        group_hiking_only_track_output_filename.write_text(gpx_2_str(group[5]))
    group_track_output_filename.write_text(gpx_2_str(group[3]))
    group_waypoint_output_filename.write_text(gpx_2_str(group[4]))
