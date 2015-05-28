import os
import file_compare
import parse_arg
import file_operation
import qcow_file_info


def main(in_cotalogue, file_json):
    if not os.path.exists(in_cotalogue) or not os.path.isdir(in_cotalogue):
        print("%s does not exists or not a directory" % in_cotalogue)
        exit(1)

    if os.path.exists(file_json) and not os.path.isfile(file_json):
        print("%s does exists but not a file" % args.dir)
        exit(1)
    old_info = file_operation.read_json(file_json)
    new_info = file_compare.transform_info(
        qcow_file_info.get_list(in_cotalogue))
    file_compare.compare_files(new_info, old_info)


if __name__ == '__main__':
    main(parse_arg.PATH_TO_INPUT_CATOLOGUE, parse_arg.PATH_TO_INPUT_FILE)
