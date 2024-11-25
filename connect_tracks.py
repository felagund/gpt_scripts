#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# on windows, build with pyinstaller --one-file connect_tracks.py

#from IPython import embed
# put embed() when one needs to embed
import itertools
#import xml.etree.ElementTree as etree
from lxml import etree
import geopy.distance as ds
import argparse
import glob
import sys
from zipfile import ZipFile
import zipfile
import io
from collections import namedtuple
from collections import defaultdict
from copy import deepcopy
import shutil
import os

Point = namedtuple('Point', ['coordinates','name','track','order'])
NS = {'': 'http://www.opengis.net/kml/2.2'}

#helper developement function to print elements
def pp(element, **kwargs):
     xml = etree.tostring(element, pretty_print=True, **kwargs)
     print(xml.decode(), end='')

# prints debug info
def print_debug(filename,object_to_print,text=""):
    with open(filename, "w") as file:
        if text:
            file.writelines(text)
        for line in object_to_print:
            file.writelines(";".join([str(i) for i in line]) + "\n")

# removes the part after comma in coordinates like -70,12345,678 - it is about 10 cm difference, takes in string and returns string - only for the y coordinate, seems like kml does not support fractions for x
def normalize(coordinates,exact=False):
    x,y = tuple(coordinates.split(",-"))
    y = "-"+y
    normalxy = []
    for c in [x,y]:
        if "," in c:
            main, remainder = c.split(",")
            if remainder == "NaN" or remainder == "nan":
                remainder = "0"
            if "." in remainder:
                remainder = remainder.split(".")[0]
            if exact:
                multiple = 0.00001
                for i in range(len(remainder)):
                    multiple *= 0.1
                normalxy.append(str(float(main) - int(remainder)*multiple))
            else:
                if int(remainder[0]) > 5:
                    normalxy.append(str(float(main) - 0.00001))
                else:
                    normalxy.append(main)
        else:
            normalxy.append(c)
    return ",".join(normalxy)

# adds comma for coordinates with more than 5 decimal places (ony for y, at least JOSM did not like fractions on x coordinate)
def add_comma(coordinates):
    x,y = tuple(coordinates.split(",-"))
    y = "-"+y
    normalxy = []
    for c in [x,y]:
        if len(c) > 9:
            cc = c[:9] + "," + c[9:]
            if len(cc) > 13:
                cc = cc[:13]
            else:
                while len(cc) < 13:
                    cc = cc +"0"
            normalxy.append(cc)
        else:
            normalxy.append(c)
    return x[:9] + "," + normalxy[1]

# shortens coordinates to (12345, 67890) to make the search for nearest point much faster
def get_short_coord(point):
    return tuple([int(i[1:3] + i[4:7]) for i in normalize(point.coordinates).split(",")])
#returns coordinates as a tuple of floats
def get_float_coord(point,exact=False):
    if exact:
        return tuple([float(i) for i in normalize(point.coordinates,exact=True).split(",")])
    else:
        return tuple([float(i) for i in normalize(point.coordinates).split(",")])

def remove_second_points(points  ,distance,p):
    # removes points that are right behind first or last point that is moved
    # and at shorter distance than by which that point is moved
    # it removes sharpt very short turns that can otherwise arise from turning
    # assumes the point that was moved is the first one
    # goes over the first 4 points only
    first = normalize(points[0])
    to_delete = []
    for i,point in enumerate(points[1:4]):
        if ds.great_circle(first,normalize(point)).m < distance:
            to_delete.append(i+1)
    to_delete.reverse()
    for i in to_delete:
        if i + 1  < len(points): 
            del(points[i])
    return points  
    
# changes a firstpoint or a lastpoint in a parent track to the point with newpoint, operating on the KML
# and removes endpoints that moved so they are not target for further changes
# and adds point with new coordinates
def change_endpoint(point_to_change,new_coordinates,distance,second_pass=False):
    # remove endpoints that moved so they are not target for further changes add point with new coordinates
    global end_points,end_points_groups,new_groups
    linepoints = point_to_change.track.text.strip().split(" ")
    if point_to_change.order == "firstpoint":
        linepoints  [0] = new_coordinates
        remove_second_points(linepoints,distance,point_to_change)
    elif point_to_change.order == "lastpoint":
        linepoints  [-1] = new_coordinates
        linepoints.reverse()
        remove_second_points(linepoints,distance,point_to_change)
        linepoints.reverse()
    point_to_change.track.text = " ".join(linepoints  )
    newpoint = Point(new_coordinates, point_to_change.name, point_to_change.track, point_to_change.order)
    end_points = end_points - set([point_to_change])
    end_points = end_points.union(set([newpoint]))
    # when a point is at the edge of square, a new point might be on a new square that does not exist yet
    if point_to_change in end_points_groups[get_short_coord(point_to_change)]:
        end_points_groups[get_short_coord(point_to_change)].remove(point_to_change)
    if get_short_coord(newpoint) in end_points_groups.keys():
        end_points_groups[get_short_coord(newpoint)].append(newpoint)
    else:
        if not second_pass:
            end_points_groups[get_short_coord(newpoint)] = [newpoint]
        else:
            new_groups[get_short_coord(newpoint)] = [newpoint]

# gets nearest point from points grouped by coordinates if it is closer than lowest_distance
def get_nearest(x,y,grouped_points, point_to_search_from,lowest_distance,current_nearest=False):
            points_to_search_list = []
            for i in [x - 1, x, x+1]:
                for ii in [y -1, y, y+1]:
                    if (i,ii) in grouped_points.keys():
                        for point in grouped_points[(i,ii)]:
                            if point.name is not point_to_search_from.name:
                                points_to_search_list.append(point)
            points_to_search = set(points_to_search_list)
            if current_nearest:
                nearest = current_nearest
            else:
                nearest = Point("nowhere","too far",None,None)
            if point_to_search_from in points_to_search:
                points_to_search.remove(point_to_search_from)
            coord = normalize(point_to_search_from.coordinates)
            for point in points_to_search:
                dd = ds.great_circle(coord,normalize(point.coordinates)).m
                if dd < lowest_distance:
                    nearest = point
                    lowest_distance = dd
            #this can happen when the difference is less than 10 cm, only in the places after comma in coordinates like -70.12345,678, we then do not need to go further
                if lowest_distance == 0:
                    break
            return(lowest_distance, nearest)

# gets a list of all points closer than a limit
def get_closest(points_to_search, point_to_search_from,limit):
            coord = normalize(point_to_search_from.coordinates)
            nearest = []
            #if point_to_search_from in points_to_search:
            #    points_to_search.remove(point_to_search_from)
            for point in points_to_search.difference({point_to_search_from}):
                dd = ds.great_circle(coord,normalize(point.coordinates)).m
                if dd < limit:
                    nearest.append(point)
            if nearest:
                nearest.append(point_to_search_from)
            return(nearest)

#split a track at appropriate midpoints
def split_track(track,midpoints):
    old_tracks = [track]
    for i,point in enumerate(midpoints):
        for old_track in old_tracks:
            if point.coordinates in old_track.text:
                split_temp = old_track.text.split(point.coordinates)
                # some tracks have same point repeated twice, which lead to split being three members, middle one being empty
                split = [s for s in split_temp if not s == " "]
                new_linestring1 = split[0] + point.coordinates
                new_linestring2 = point.coordinates + split[1]
                placemark = old_track.getparent().getparent()
                new1 = deepcopy(placemark)
                new2 = deepcopy(placemark)
                new_track1 = new1.find(".//LineString/coordinates",NS)
                new_track1.text = new_linestring1
                new_track2 = new2.find(".//LineString/coordinates",NS)
                new_track2.text = new_linestring2
                # if we wanted to manipulate name, something like this
                #new2.find(".//name",NS).text = new2.find(".//name",NS).text + " " + str(i)
                old_tracks.remove(old_track)
                old_tracks.extend([new_track1,new_track2])
                placemark.addprevious(new1)
                placemark.addnext(new2)
                placemark.getparent().remove(placemark)
                break


#this reads the kml and sets up data structures
def read_kml():
    # this gets all the tracks and only their coordinates
    tracks_folder = [a for a in k.findall(".//Folder",NS) if a.find("./name",NS).text == "Tracks" ][0]
    tracks = tracks_folder.findall(".//LineString/coordinates/../..", NS)
    # creates a list of endpoints
    mid_points_list = []
    end_points_list = []
    print("Sorting points")
    for track in tracks:
        linepoints = [a.strip() for a in track.find(".//LineString/coordinates",NS).text.split(" ") if a.strip()]
        name = track.find(".//name",NS).text
        end_points_list.append(Point(linepoints[0],name,track.find(".//LineString/coordinates",NS),"firstpoint"))
        end_points_list.append(Point(linepoints[-1],name,track.find(".//LineString/coordinates",NS),"lastpoint"))
        for point in linepoints[1:-1]:
            mid_points_list.append(Point(point,name,track.find(".//LineString/coordinates",NS),"middlepoint"))

    # dicts for searching nearest endpoint or point, optimization for making things faster
    end_points_groups = dict()
    mid_points_groups = dict()
    print("Grouping end points")
    for point in end_points_list:
        cor = get_short_coord(point)
        if cor not in end_points_groups.keys():
            end_points_groups[cor] = [point]
        else:
            end_points_groups[cor].append(point)

    print("Grouping all points")
    for point in mid_points_list:
        cor = get_short_coord(point)
        if cor not in mid_points_groups.keys():
            mid_points_groups[cor] = [point]
        else:
            mid_points_groups[cor].append(point)
    return end_points_groups,mid_points_groups,end_points_list

#arguments on the command line
parser = argparse.ArgumentParser()
parser.add_argument("-i","--input_file", help='Input KMZ file, defaults to "GPT Master (anynumber).kmz" and if such KMZ file is not found, to any KMZ file in the working directory')
parser.add_argument("-o","--output_file", help='Output KMZ file, defaults to "INPUT_FILE_connected_endpoints.kmz"')
parser.add_argument("--debug", help="If set, prints out debug files", action="store_true")
parser.add_argument("-sst" , "--skip_splitting_tracks", help="If set, breaks a track when endpoint of another track is the middle the first track, only works when first step not skipped", action="store_true")
parser.add_argument("-s1", "--skip_first", help="If set, skips the first pass", action="store_true")
parser.add_argument("-s2", "--skip_second", help="If set, skips the second pass", action="store_true")
parser.add_argument("-l1", "--first_pass_limit", help="Sets maximum distance under which consecutive points will be moved in first pass (default 35 m) (for nonconsecutive endpoints 75 percent of the value is used, for midpoints, second pass limit is used", type=int, default=35)
parser.add_argument("-l2", "--second_pass_limit", help="Sets maximum distance under which points will be moved in second pass (default 10 m)", type=int, default=10)
args = parser.parse_args()

# only do anything when both steps are not skipped
if not args.skip_first or not args.skip_second:
    #open the file
    if args.input_file:
        input_file = args.input_file
    else:
        kmzs = glob.glob('./GPT Master (*).kmz')
        if not kmzs:
            kmzs = glob.glob('./*.kmz')
        if len(kmzs) > 1:
                kmzs.sort(reverse=True)
        if kmzs:
            input_file = kmzs[0]
        else:
            sys.exit("No KMZ file (with extension lowercase kmz) in current directory and none specified on command line, exiting")

    print("Opening file: " + input_file)
    with ZipFile(input_file) as zfile:
        with zfile.open(zfile.namelist()[0]) as readfile:
            kk = io.TextIOWrapper(readfile, encoding="utf-8")
            k = etree.parse(kk).getroot()

if not args.skip_first:
    end_points_groups,mid_points_groups,end_points_list = read_kml()
    # creates consecutive pairs of endpoints to iterate over
    pairs = itertools.pairwise(end_points_list)
    end_points = set(end_points_list)
    equal_to_next = False
    limit = args.first_pass_limit
    hundred_percent = str(len(end_points_list) - 1)
    # collect stats
    new_groups = dict()
    same =  []
    small = []
    non_consecutive_same = []
    non_consecutive_small = []
    close_but_not_enough = []
    too_far = []
    tracks_to_split = defaultdict(list)
    """
    for each pair first checks if the second was set to equal to the first in the previous step, if so, it goes to another pair because this pair will be the same at the end
    then it checks if the second is equal to first, there is nothing to do then as the points are already connected
    then if the distance between the first and second is less than 20 metres, it sets the first to be equal to the second as they are probably meant to be connected
    """
    print("Running first pass:")
    for iii, pair in enumerate(pairs):
        print(str(iii+1)+"/"+hundred_percent+"\r", end='', flush=True)
        point1,point2 = pair[0],pair[1]
        if equal_to_next:
            equal_to_next = False
        elif point1.coordinates == point2.coordinates:
            equal_to_next = True
            same.append((point1.coordinates, point2.coordinates, point1.name, point2.name))
        else:
            other_end_points = end_points - set([point1])
            other_end_points_coord = set([point.coordinates for point in other_end_points])
            d = ds.great_circle(normalize(point1.coordinates),normalize(point2.coordinates)).m
            if point1.coordinates in other_end_points_coord:
                non_consecutive_same.append((point1.coordinates,point1.name,point1.order))
            elif d < limit:
                # when the points belong to the same track, o not mak them the same unless they can form a square (so by making two the same, a tringle can arise
                if (not point1.name == point2.name) and (len(point1.track.text.split(" ")) > 2):
                    change_endpoint(point1,point2.coordinates,d)
                    equal_to_next = True
                    small.append((d, point1.coordinates, point2.coordinates, point1.name, point2.name,point1.order,point2.order))
            else:
                # optimization to only search in areas neighbouring the endpoint
                x1,y1 = get_short_coord(point1)
                lowest_distance,nearest_point = get_nearest(x1,y1,end_points_groups,point1,5000)
                if lowest_distance > limit * 0.75:
                    lowest_distance,nearest_point = get_nearest(x1,y1,mid_points_groups,point1,lowest_distance,current_nearest=nearest_point)
                if point1.coordinates == nearest_point.coordinates:
                    non_consecutive_same.append((point1.coordinates,nearest_point.coordinates,point1.name,nearest_point.name,point1.order,nearest_point.order))
                elif lowest_distance < args.second_pass_limit:
                    change_endpoint(point1,nearest_point.coordinates,lowest_distance)
                    non_consecutive_small.append((lowest_distance, point1.coordinates,nearest_point.coordinates,point1.name,nearest_point.name,point1.order,nearest_point.order))
                elif lowest_distance < 100:
                    close_but_not_enough.append((lowest_distance, point1.coordinates,nearest_point.coordinates,point1.name,nearest_point.name,point1.order,nearest_point.order))
                elif lowest_distance < 5000:
                    too_far.append((lowest_distance, point1.coordinates,nearest_point.coordinates,point1.name,nearest_point.name,point1.order,nearest_point.order))
                else:
                    too_far.append((lowest_distance, point1.coordinates,point1.name))
                if not args.skip_splitting_tracks and nearest_point.order == "middlepoint" and lowest_distance < args.second_pass_limit:
                    tracks_to_split[nearest_point.track].append(nearest_point)
    print(str(iii+1)+"/"+hundred_percent+"\r")

    if not args.skip_splitting_tracks:
        splitted = []
        print("Splitting tracks")
        hundred_percent = str(len(tracks_to_split))
        for iii, track in enumerate(tracks_to_split):
            print(str(iii+1)+"/"+hundred_percent+"\r", end='', flush=True)
            splitted.append((tracks_to_split[track][0].name,len(tracks_to_split[track])))
            split_track(track,tracks_to_split[track])
        print(str(iii+1)+"/"+hundred_percent+"\r")

if not args.skip_second:
    """all endpoints are divided into squares, in each square, points that are close to each other are grouped and when they are under limit, moved on top of each other"""
    print("Starting second pass")
    end_points_groups,mid_points_groups, end_points_list = read_kml()
    hundred_percent = str(len(end_points_groups))
    end_points = set(end_points_list)
    print("Running second pass:")
    grouped_by_closenes = []
    not_moved = []
    new_groups = dict()
    for iii, group in enumerate(end_points_groups):
            print(str(iii+1)+"/"+hundred_percent+"\r", end='', flush=True)
            x,y = group
            points_to_search_list = []
            for i in [x - 1, x, x+1]:
                for ii in [y -1, y, y+1]:
                    if (i,ii) in end_points_groups.keys():
                        points_to_search_list.extend(end_points_groups[(i,ii)])
            points_to_search = set(points_to_search_list)
            points_to_move = []
            for point in end_points_groups[group]:
                if point not in points_to_move:
                    closest = get_closest(points_to_search,point,args.second_pass_limit)
                    if closest:
                        coords = []
                        for close_point in closest:
                            coords.append(get_float_coord(close_point,exact=True))
                        unique_coords = set(coords)
                        if len(unique_coords) > 1:
                            xx = [i[0] for i in unique_coords]
                            yy = [i[1] for i in unique_coords]
                            xavg = sum(xx)/len(xx)
                            yavg = sum(yy)/len(yy)
                            avg = add_comma(",".join([str(xavg), str(yavg)]))
                            for close_point in closest:
                                distance = ds.great_circle(normalize(avg,exact=True),normalize(close_point.coordinates,exact=True)).m
                                grouped_by_closenes.append((distance, close_point.coordinates, close_point.name, close_point.order, avg))
                                points_to_move.append(close_point)
            for point in points_to_move:
                change_endpoint(point,avg,distance,second_pass=True)
    print(str(iii + 1)+"/"+hundred_percent+"\r")


if args.skip_first and args.skip_second:
    print("Both passes skipped, nothing was done")
else:
    #open the file
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = input_file[:-4] + "_connected_endpoints.kmz"
    print("Writing to file: " + output_file)
    mf = io.BytesIO()
    with ZipFile(mf, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('doc.kml', etree.tostring(k, encoding="unicode"))
    with open(output_file, "wb") as f:
        f.write(mf.getvalue())

    if args.debug:
        print("Writing debug info into directory debug_connect_tracks_py, overwriting if it already exists")
        dirname = 'debug_connect_tracks_py'
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)
        print_debug(dirname + "/small.txt", small,"Moved by a short distance lower than " + str(args.first_pass_limit) + "m \n")
        print_debug(dirname + "/non_consecutive_same.txt", non_consecutive_same, "Points are the same as some other endpoint but not consecutive\n")
        print_debug(dirname + "/non_consecutive_small.txt", non_consecutive_small, "Moved point to non-consecutive point closer than " + str(args.second_pass_limit) + "m \n")
        print_debug(dirname + "/close_but_not_enough.txt", close_but_not_enough, "Distance to nearest point is lower than 100 m but higher then " + str(args.second_pass_limit) + "m \n")
        print_debug(dirname + "/too_far.txt", too_far, "Nearest end-point too far\n")
        if not args.skip_splitting_tracks:
            print_debug(dirname + "/splitted.txt", splitted, "Tracks splitted into several chunks\n")
        if not args.skip_second:
            print_debug(dirname + "/second_pass_moved.txt", grouped_by_closenes,"Points moved in second pass that are closer to each other than "+ str(args.second_pass_limit) + "m \n")
