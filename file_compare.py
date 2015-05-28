import os
import json
import parse_arg
import qcow_file_info as qcow
import file_operation
import sys


def transform_info(new_list):
    result = {}
    for info in new_list:
            result[info['filename']] = info
    return result


def compare_files(new_list, old_list):
    new_file_list = set([new_list[e]['filename'] for e in new_list])
    old_file_list = set([old_list[e]['filename'] for e in new_list])
    deleted = old_file_list - new_file_list
    added = new_file_list - old_file_list
    common = new_file_list & old_file_list

    if added:
        print("%s file(s) was deleted\n" % (str(len(deleted))))
        print('\n'.join(created_files))
        print('')

    if deleted:
        print("%s file(s) was deleted\n" % (str(len(deleted))))
        print('\n'.join(created_files))
        print('')

    for elem in common:
        changes = compare_file_info(new_list[elem], old_list[elem])
        if changes:
            print('[%s] changed:' % elem)
            print('\n'.join(changes))

    # # Will know witch file was added and deleted
    # name_list_old = []
    # name_list_new = []
    # for element_ol in old_list:
    #     name_list_old.append(element_ol['filename'])
    # for element_nl in new_list:
    #     name_list_new.append(element_nl['filename'])
    #     deleted = set(name_list_old) - set(name_list_new)
    # if deleted:
    #     sys.stdout.write("%s file(s) was deleted\n" % (str(len(deleted))))
    #     print '\n'.join(deleted)
    #     for i in deleted:
    #         sys.stdout.write("%s\n" % i)
    # added = set(name_list_new) - set(name_list_old)
    # if added:
    #     sys.stdout.write("%s file(s) was added\n" % (str(len(added))))
    #     for i in added:
    #         sys.stdout.write("%s\n" % i)
    # # delete files that have been added in order not to treat them as mutable
    # for elem in added:
    #     for diction in new_list:
    #         if diction['filename'] == elem:
    #             new_list.remove(diction)
    # return new_list


# def walk_through_lists(new_list, old_list):
#     # find files witch have same names and compare its backing file and snaps
#     for n_item in new_list:
#         for o_item in old_list:
#             if n_item['filename'] == o_item['filename']:
#                 compare_backing(n_item, o_item)
#                 compare_snap(n_item, o_item)


# def compare_backing(new_dict, old_dict):
#     o_backing = None
#     n_backing = None
#     if 'backing_file' in new_dict.keys():
#         n_backing = new_dict['backing_file']
#     if 'backing_file' in old_dict.keys():
#         o_backing = old_dict['backing_file']
#     if n_backing:
#         if o_backing:
#             # check if backingfile was changed
#             if n_backing != o_backing:
#                 sys.stdout.write("In file %s was changed backing file: old - %s, new - %s .\n" % (
#                     str(new_dict['backing_file']),
#                     str(o_backing),
#                     str(n_backing)))
#         else:
#             # check if backingfile was added
#             sys.stdout.write("In file %s was added backing file %s .\n" % (
#                 str(new_dict['filename']),
#                 str(n_backing)))
#     elif o_backing:
#         # check if backingfile was deleted
#         sys.stdout.write("In file %s was deleted backing file %s .\n" % (
#             str(new_dict['filename']),
#             str(o_backing)))


def compare_file_info(newfile, oldfile):
    """Compare two info dicts"""
    changes = []
    tmp = '[%s]\t%s\twas %s'
    tmpcommon = '[%s]\t was changed \told\t%s\t new\t%s'

    new_keys = set([key for key in newfile if key != 'snapshots'])
    old_keys = set([key for key in oldfile if key != 'snapshots'])
    deleted_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    common_keys = new_keys & old_keys

    for key in deleted_keys:
        changes.append(tmp % (key, oldfile[key], 'deleted'))

    for key in added_keys:
        changes.append(tmp % (key, newfile[key], 'added'))

    for key in common_keys:
        if oldfile[key] != newfile[key]:
            changes.append(tmpcommon % (key, oldfile[key], newfile[key]))

    if 'snapshots' in newfile or 'snapshots' in oldfile:
        changes.extend(compare_snap(newfile.get('snapshots', []),
                                    oldfile.get('snapshots', [])))

    return changes


def compare_snap(newsnap, oldsnap):
    changes = []
    tmp = '[%s]\t%s\twas %s'
    tmpcommon = '[%s]\t was changed \told %s\t new %s'
    _new_snap = {snap['id']: snap for snap in newsnap}
    _old_snap = {snap['id']: snap for snap in oldsnap}
    new_keys = set([key for key in _new_snap])
    old_keys = set([key for key in _old_snap])
    deleted_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    common_keys = new_keys & old_keys

    name = lambda snap: (('name:' + snap['name']) if snap['name']
                         else ('id:' + snap['id']))

    for key in deleted_keys:
        _name = name(_old_snap[key])
        changes.append(tmp % ('snapshot', _name, 'deleted'))

    for key in added_keys:
        _name = name(_new_snap[key])
        changes.append(tmp % ('snapshot', _name, 'was added'))

    for key in common_keys:
        if _old_snap[key]['name'] != _new_snap[key]['name']:
            changes.append(tmpcommon % ('snapshot name',
                                        name(_old_snap[key]),
                                        name(_new_snap[key])))
        elif _old_snap[key]['virtualsize'] != \
                _new_snap[key]['virtualsize']:
            changes.append(tmpcommon % ('snapshots ' + name(_old_snap[key]) +' virtualsize ',
                                        _old_snap[key]['virtualsize'],
                                        _new_snap[key]['virtualsize']))

    return changes


# def compare_snap(new_dict, old_dict):
#     changes = []
#     if 'snapshots' in new_dict.keys():
#         n_snap = new_dict['snapshots']
#     if 'snapshots' in old_dict.keys():
#         o_snap = old_dict['snapshots']
#     if n_snap:
#         if o_snap:
#             # snaps were in this file when was created json file and now too
#             id_list_old = []
#             id_list_new = []
#             for element_ol in o_snap:
#                 id_list_old.append(element_ol['id'])
#             for element_nl in n_snap:
#                 id_list_new.append(element_nl['id'])
#             deleted_sn = set(id_list_old) - set(id_list_new)
#             if deleted_sn:
#                 sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
#                     str(len(deleted_sn)),
#                     new_dict['filename']))
#                 print_sn(deleted_sn, n_snap)
#             added_sn = set(id_list_new) - set(id_list_old)
#             if added_sn:
#                 sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
#                     str(len(added_sn)),
#                     new_dict['filename']))
#                 print_sn(added_sn, n_snap)
#             for elem in added_sn:
#                 for diction in n_snap:
#                     if diction['id'] == elem:
#                         n_snap.remove(diction)
#             if n_snap:
#                 compare_same_sn(n_snap, o_snap, new_dict)
#         else:
#             # check if in this file wasn't snaps and they were added
#             sys.stdout.write("%s snapshot(s) was added in %s:\n" % (
#                 str(len(n_snap)),
#                 new_dict['filename']))
#             print_sn(n_snap, n_snap)
#     elif o_snap:
#         # check if in this file was snaps, but now they were deleted
#             sys.stdout.write("%s snapshot(s) was deleted in %s:\n" % (
#                 str(len(o_snap)),
#                 new_dict['filename']))
#             print_sn(o_snap, n_snap)


# def print_sn(snap_ids, list_snap):
#     for sn_id in snap_ids:
#         for elem in list_snap:
#             if sn_id == elem['id']:
#                 sys.stdout.write("%s\n" % str(elem))


# def compare_same_sn(new_list, old_list, curent_snap):
#     for new in new_list:
#         for old in old_list:
#             if new['id'] == old['id']:
#                 if new['name'] != old['name']:
#                     sys.stdout.write("In file with name %s snapshot with id %s was changed name: old - %s, new - %s \n" % (
#                         str(curent_snap['filename']),
#                         str(new['id']),
#                         str(old['name']),
#                         str(new['name'])))
#                 if new['virtualsize'] != old['virtualsize']:
#                     sys.stdout.write("In file with name %s snapshot with id %s was changed virtual size: old - %s, new - %s \n" % (
#                         str(curent_snap['filename']),
#                         str(new['id']),
#                         str(old['virtualsize']),
#                         str(new['virtualsize'])))
