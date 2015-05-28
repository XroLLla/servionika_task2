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
