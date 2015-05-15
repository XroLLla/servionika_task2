import os
import file_compare
import parse_arg
import file_operation
import qcow_file_info


def main(in_cotalogue, file_json):
    old_info = file_operation.read_json(file_json)
    # check availability of file with information about json files
    if old_info is not None:
        list_of_file_info = qcow_file_info.get_list(in_cotalogue, file_json)
        # check path to catalog
        if list_of_file_info is not None:
            list_of_file_info = file_compare.compare_files_name(
                list_of_file_info,
                old_info)
            file_compare.walk_through_lists(list_of_file_info, old_info)
        else:
            print "Error with file or path to catalogue"
    else:
        print "Error with file "


if __name__ == '__main__':
    main(parse_arg.PATH_TO_INPUT_CATOLOGUE, parse_arg.PATH_TO_INPUT_FILE)
