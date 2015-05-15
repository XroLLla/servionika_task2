import os
import json
import parse_arg
import qcow_file_info as qcow
import file_operation
import sys


def compare_files_name(new_list, old_list):
    # Will know with file was added and deleted
    name_list_old = []
    name_list_new = []
    for element_ol in old_list:
        name_list_old.append(element_ol['filename'])
    for element_nl in new_list:
        name_list_new.append(element_nl['filename'])
        deleted = set(name_list_old) - set(name_list_new)
    if deleted:
        sys.stdout.write("%s file(s) was deleted\n" % (str(len(deleted))))
        for i in deleted:
            sys.stdout.write("%s\n" % i)
    added = set(name_list_new) - set(name_list_old)
    if added:
        sys.stdout.write("%s file(s) was added\n" % (str(len(added))))
        for i in added:
            sys.stdout.write("%s\n" % i)
    for elem in added:
        for diction in new_list:
            if diction['filename'] == elem:
                new_list.remove(diction)
    return new_list


def compare_same_sn(new_list, old_list, curent_snap):
    for new in new_list:
        for old in old_list:
            if new['id'] == old['id']:
                if new['name'] != old['name']:
                    sys.stdout.write("In file with name %s snapshot with id %s was changed name: old - %s, new - %s \n" % (
                        str(curent_snap['filename']),
                        str(new['id']),
                        str(old['name']),
                        str(new['name'])))
                if new['virtualsize'] != old['virtualsize']:
                    sys.stdout.write("In file with name %s snapshot with id %s was changed virtual size: old - %s, new - %s \n" % (
                        str(curent_snap['filename']),
                        str(new['id']),
                        str(old['virtualsize']),
                        str(new['virtualsize'])))


def walk_through_lists(new_list, old_list):
    for n_item in new_list:
        for o_item in old_list:
            if n_item['filename'] == o_item['filename']:
                compare_backing(n_item, o_item)
                compare_snap(n_item, o_item)


def compare_backing(new_dict, old_dict):
    o_backing = None
    n_backing = None
    if 'backing_file' in new_dict.keys():
        n_backing = new_dict['backing_file']
    if 'backing_file' in old_dict.keys():
        o_backing = old_dict['backing_file']
    if n_backing is not None:
        if o_backing is not None:
            if n_backing != o_backing:
                sys.stdout.write("In file %s was changed backing file: old - %s, new - %s .\n" % (
                    str(new_dict['backing_file']),
                    str(o_backing),
                    str(n_backing)))
        else:
            sys.stdout.write("In file %s was added backing file %s .\n" % (
                str(new_dict['filename']),
                str(n_backing)))
    elif o_backing is not None:
        sys.stdout.write("In file %s was deleted backing file %s .\n" % (
            str(new_dict['filename']),
            str(o_backing)))


def compare_snap(new_dict, old_dict):
    o_snap = []
    n_snap = []
    if 'snapshots' in new_dict.keys():
        n_snap = new_dict['snapshots']
    if 'snapshots' in old_dict.keys():
        o_snap = old_dict['snapshots']
    if n_snap:
        if o_snap:
            id_list_old = []
            id_list_new = []
            for element_ol in o_snap:
                id_list_old.append(element_ol['id'])
            for element_nl in n_snap:
                id_list_new.append(element_nl['id'])
            deleted_sn = set(id_list_old) - set(id_list_new)
            if deleted_sn:
                sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
                    str(len(deleted_sn)),
                    new_dict['filename']))
                print_sn(deleted_sn, n_snap)
            added_sn = set(id_list_new) - set(id_list_old)
            if added_sn:
                sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
                    str(len(added_sn)),
                    new_dict['filename']))
                print_sn(added_sn, n_snap)
            for elem in added_sn:
                for diction in n_snap:
                    if diction['id'] == elem:
                        n_snap.remove(diction)
            if n_snap:
                compare_same_sn(n_snap, o_snap, new_dict)
        else:
            sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
                str(len(n_snap)),
                new_dict['filename']))
            print_sn(n_snap, n_snap)
    elif o_snap:
            sys.stdout.write("%s snapshot(s) was deleted in %s:\n" % (
                str(len(o_snap)),
                new_dict['filename']))
            print_sn(o_snap, n_snap)


def print_sn(snap_ids, list_snap):
    for sn_id in snap_ids:
        for elem in list_snap:
            if sn_id == elem['id']:
                sys.stdout.write("%s\n" % str(elem))


def get_list(in_cotalogue, filejson):
    # check path to cotalogue
    if os.path.exists(in_cotalogue):
        if os.path.isfile(filejson):
            # check path to out_file
            list_of_dict = []
            for d, dirs, files in os.walk(parse_arg.PATH_TO_INPUT_CATOLOGUE):
                for f in files:
                    with open(os.path.join(d, f), "rb") as binary_file:
                        # check qcow2 file
                        byte = binary_file.read(3)
                        if byte == "QFI":
                            fileqcow = os.path.join(d, f)
                            list_of_dict.append(qcow.get_qcow_file_dict(fileqcow))

        else:
            print "Wrong path to the file"
            return None
    else:
        print "No such directory"
        return None
    return list_of_dict