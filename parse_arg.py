import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--path_to_file", type=str,
                    required=True,
                    help="this is path to directory whith you want scan")
parser.add_argument("-d", "--path_to_catologue", type=str,
                    required=True,
                    help="this is path to the output file")
args = parser.parse_args()

PATH_TO_INPUT_CATOLOGUE = args.path_to_catologue
PATH_TO_INPUT_FILE = args.path_to_file
