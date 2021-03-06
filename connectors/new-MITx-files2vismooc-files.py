# /usr/bin/env python
"""
The purpose of this script is to transform the new MITx course data
files into the course files required by vismooc pipe of MOOC-Learner-Curated.

Note that the fields in the course files generated by this script can
only be a subset of the fields that vismooc files have. However, those subset
of fields are sufficient to run thought vismooc pipe of MLC.

Also note that since some required fields are missing in new MITx data tables
this script populate these fields by nulls.
"""
import io
import os.path
import json
import csv
import datetime

FILE_INPUT = {
    'course_axis': 'course_axis.json',
    'course_item': 'course_item.json',
    'chapter_grades': 'chapter_grades.json',
    'user_info_combo': 'user_info_combo.json',
    'forum': 'forum.json',
}

FILE_OUTPUT = {
    'structure': 'course_structure-prod-analytics.json',
    'certificate': 'certificates_generatedcertificate-prod-analytics.sql',
    'enrollment': 'student_courseenrollment-prod-analytics.sql',
    'user': 'auth_user-prod-analytics.sql',
    'profile': 'auth_userprofile-prod-analytics.sql',
    'forum': 'prod.mongo',
}

MAP_DICT = {
    'structure': [
        (
            (0, 0),
            'course_axis',
            {
                # 'id' filed is temporary and will be picked out by next mapping
                u'id': u'url_name',
                u'category': u'category',
            }
        ),
        (
            (0, 1),
            'course_axis',
            {
                u'metadata': lambda d: UNIT_MAP_WRAP_METADATA(d)
            }
        ),
        (
            (0, 2),
            'course_axis',
            {
                u'children': lambda d, dicts: [od[u'url_name']
                                               if u'url_name' in od
                                               else report(od)
                                               for od in dicts
                                               if u'parent' in od and od[u'parent'] == d[u'url_name']
                                               ] if u'url_name' in d else report(d)
            }
        )

    ],
    'certificate': [
        (
            (0, 0),
            'user_info_combo',
            {
                # 'id' field not sure
                u'id': u'id_map_hash_id',
                u'user_id': u'user_id',
                u'course_id': u'certificate_course_id',
            }
        ),
        (
            (0, 1),
            'user_info_combo',
            {
                u'grade': lambda d: d[u'certificate_grade']
                                    if u'certificate_grade' in d
                                    else '0',
                u'created_date': lambda d: UNIT_MAP_CONVERT_TIMESTAMP(
                    TIMESTAMP_FORMAT['in'],
                    TIMESTAMP_FORMAT['certificate'],
                    d[u'certificate_created_date']
                ) if u'certificate_created_date' in d else report(d),
            }
        )
    ],
    'enrollment': [
        (
            (0, 1),
            'user_info_combo',
            {
                u'created': lambda d: UNIT_MAP_CONVERT_TIMESTAMP(
                    TIMESTAMP_FORMAT['in'],
                    TIMESTAMP_FORMAT['enrollment'],
                    d[u'certificate_created_date']
                ) if u'certificate_created_date' in d else report(d),
            }
        ),
        (
            (0, 0),
            'user_info_combo',
            {
                # 'id' field not sure
                u'id': u'id_map_hash_id',
                u'user_id': u'user_id',
                u'course_id': u'enrollment_course_id',
                u'is_active': u'enrollment_is_active',
            }
        )
    ],
    'user': [
        (
            (0, 0),
            'user_info_combo',
            {
                u'id': u'user_id',
                u'username': u'username',
            }
        )
    ],
    'profile': [
        (
            (0, 0),
            'user_info_combo',
            {
                u'id': u'user_id',
                u'name': u'profile_name',
                u'language': u'profile_language',
                u'location': u'profile_location',
                u'year_of_birth': u'profile_year_of_birth',
                u'level_of_education': u'profile_level_of_education',
                u'goals': u'profile_goals',
                u'gender': u'profile_gender',
                u'country': None,
            }
        )

    ],
    'forum': [
        (
            (0, 1),
            'forum',
            {
                u'_id': lambda d: {
                    u'$oid': d[u'mongoid'] if u'mongoid' in d else report(d)
                },
                u'created_at': lambda d: {
                    u'$date': UNIT_MAP_CONVERT_TIMESTAMP(
                        TIMESTAMP_FORMAT['in'],
                        TIMESTAMP_FORMAT['forum'],
                        d[u'created_at']
                    ) if u'created_at' in d else report(d),
                },
                u'updated_at': lambda d: {
                    u'$date': UNIT_MAP_CONVERT_TIMESTAMP(
                        TIMESTAMP_FORMAT['in'],
                        TIMESTAMP_FORMAT['forum'],
                        d[u'updated_at']
                    ) if u'updated_at' in d else report(d),
                },
                u'comment_thread_id': lambda d: {
                    u'$oid': d[u'comment_thread_id'] if u'comment_thread_id' in d else report(d)
                },
                u'parent_id': lambda d: {
                    u'$oid': d[u'parent_id'] if u'parent_id' in d else report(d)
                },

            }
        ),
        (
            (0, 0),
            'forum',
            {
                u'course_id': u'course_id',
                u'author_id': u'author_id',
                u'body': u'body',
                u'_type': u'_type',
                u'title': u'title',
                u'thread_type': u'thread_type',
            }
        )

    ],
}


def UNIT_MAP_WRAP_METADATA(d):
    if u'category' not in d:
        return []
    if d[u'category'] == u'course':
        return {
            u'display_name': d[u'name'] if u'name' in d else report(d),
            u'start': UNIT_MAP_CONVERT_TIMESTAMP(
                TIMESTAMP_FORMAT['in'],
                TIMESTAMP_FORMAT['structure'],
                d[u'start']
            ) if u'start' in d else report(d),
            u'end': UNIT_MAP_CONVERT_TIMESTAMP(
                TIMESTAMP_FORMAT['in'],
                TIMESTAMP_FORMAT['structure'],
                d[u'due']
            ) if u'due' in d else report(d),
        }
    elif d[u'category'] == u'video':
        return {
            u'display_name': d[u'name'] if u'name' in d else report(d),
            # the html path is missed (not sure)
            u'html5_sources': [],
            # record youtube id to hope for extension of vismooc pipe
            u'youtube_id_1_0': d[u'data'][u'ytid']
            if u'data' in d and u'ytid' in d[u'data'] else report(d)
        }
    else:
        return {
            u'display_name': d[u'name'] if u'name' in d else report(d),
        }


def UNIT_MAP_CONVERT_TIMESTAMP(in_format, out_format, timestamp):
    if not timestamp:
        return None
    dt = datetime.datetime.strptime(timestamp, in_format)
    return dt.strftime(out_format)


def UNIT_MAP_IDENTICAL(x):
    return x


POST_PROCESS_MAP_DICT = {
    'structure': [
        (
            (2, 2),
            'structure',
            lambda dicts: [
                {d[u'id']: {f: d[f] for f in d if f != u'id'}
                 if u'id' in d else report(d)
                 for d in dicts}
            ]

        )
    ],
    'certificate': [
        (
            (2, 2),
            'certificate',
            UNIT_MAP_IDENTICAL,
        )
    ],
    'enrollment': [
        (
            (2, 2),
            'enrollment',
            UNIT_MAP_IDENTICAL,
        )
    ],
    'user': [
        (
            (2, 2),
            'user',
            UNIT_MAP_IDENTICAL,
        )
    ],
    'profile': [
        (
            (2, 2),
            'profile',
            UNIT_MAP_IDENTICAL,
        )
    ],
    'forum': [
        (
            (2, 2),
            'forum',
            UNIT_MAP_IDENTICAL,
        )
    ],
}

TIMESTAMP_FORMAT = {
    'in': '%Y-%m-%d %H:%M:%S UTC',
    'structure': '%Y-%m-%dT%H:%M:%SZ',
    # the microsecond is missed in input
    'forum': '%Y-%m-%dT%H:%M:%S.000Z',
    'certificate': '%Y-%m-%d %H:%M:%S',
    'enrollment': '%Y-%m-%d %H:%M:%S',
}


def raise_report(anything, flag=True):
    global typedict
    if flag in typedict:
        typedict[flag] += 1
    else:
        typedict[flag] = 1
    global count
    count += 1


def report(anything, flag=True):
    global count
    count += 1
    if flag:
        pass
        # print(flag)
        # print(anything)
    return None


def get_fields(dicts):
    if not dicts:
        return []
    if not isinstance(dicts, list) \
            or not isinstance(dicts[0], dict):
        raise ValueError("Invalid dicts")
    fields = sorted(list(dicts[0].keys()))
    for d in dicts:
        if sorted(list(d.keys())) != fields:
            raise ValueError("Invalid dicts")
    return fields


def loading(dir_path, file_input):
    if not os.path.isdir(dir_path):
        raise ValueError("Invalid input path")
    dir_path = os.path.abspath(dir_path)
    return {_input: load_file(os.path.join(dir_path + '/' + file_input[_input]))
            for _input in file_input}


def load_file(path):
    with open(path, 'r') as json_file:
        json_lines = json_file.readlines()
        dicts = [json.loads(x) for x in json_lines]
    return dicts


def saving(dir_path, file_output, output_collection):
    if not os.path.isdir(dir_path):
        raise ValueError("Invalid input path")
    dir_path = os.path.abspath(dir_path)
    if not all(_output in output_collection for _output in file_output):
        raise ValueError("Insufficient output_dict")
    for _output in file_output:
        save_file(os.path.join(dir_path + '/' + file_output[_output]),
                  output_collection[_output])


def save_file(path, dicts):
    if path.endswith('.json') or path.endswith('.mongo'):
        save_json(path, dicts)
    elif path.endswith('.sql'):
        save_csv(path, dicts)


def save_json(path, dicts):
    with io.open(path, 'w', encoding='utf8') as json_file:
        for d in dicts:
            json_file.write(
                json.dumps(d,
                           indent=4 if path.endswith('.json') else None,
                           ensure_ascii=False
                           )
                + u'\n'
            )


def save_csv(path, dicts):
    fields = get_fields(dicts)
    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(
            csv_file,
            delimiter='\t' if path.endswith('.sql')
            else ',',
            fieldnames=fields,
            quotechar='"',
            escapechar='\\',
            lineterminator='\n')
        writer.writerow({f: f.encode('utf-8')
                         if isinstance(f, unicode)
                         else f
                         for f in fields})
        for d in dicts:
            writer.writerow({f: d[f].encode('utf-8')
                             if isinstance(d[f], unicode)
                             else d[f]
                             for f in fields})


def mapping(input_collection, map_dict):
    return {_output: [map_unit(
        map_obj[0],
        input_collection[map_obj[1]],
        map_obj[2]
    )
        for map_obj in map_dict[_output]]
        for _output in map_dict}


def map_unit(order, dicts, unit_map):
    if order == (0, 0):
        return map_unit_0_0(dicts, unit_map)
    elif order == (0, 1):
        return map_unit_0_1(dicts, unit_map)
    elif order == (0, 2):
        return map_unit_0_2(dicts, unit_map)
    elif order == (2, 2):
        return map_unit_2_2(dicts, unit_map)
    else:
        raise ValueError("Invalid map order")


def map_unit_0_0(dicts, unit_map):
    return [{f: d[unit_map[f]] if unit_map[f] in d else raise_report(d, unit_map[f])
             for f in unit_map}
            for d in dicts]


def map_unit_0_1(dicts, unit_map):
    return [{f: unit_map[f](d)
             for f in unit_map}
            for d in dicts]


def map_unit_0_2(dicts, unit_map):
    return [{f: unit_map[f](d, dicts)
             for f in unit_map}
            for d in dicts]


def map_unit_2_2(dicts, unit_map):
    return unit_map(dicts)


def concatenating(mapped_collection):
    return {_output: concat_dicts(mapped_collection[_output])
            for _output in mapped_collection}


def all_disjoint(sets):
    union = set()
    for s in sets:
        for x in s:
            if x in union:
                return False
            union.add(x)
    return True


def concat_dict(list_of_dict):
    if not all(isinstance(d, dict) for d in list_of_dict):
        raise ValueError("Invalid list_of_dict")
    if not all_disjoint([set(d.keys()) for d in list_of_dict]):
        raise ValueError("Illegal concatenation of list_of_dict")
    sd = {}
    for d in list_of_dict:
        sd.update(d)
    return sd


def concat_dicts(list_of_dicts):
    if not list_of_dicts:
        return []
    if not all(len(dicts) == len(list_of_dicts[0])
               for dicts in list_of_dicts):
        raise ValueError("Illegal concatenation of list_of_dicts")
    return [concat_dict([list_of_dicts[x][y]
                         for x in range(len(list_of_dicts))])
            for y in range(len(list_of_dicts[0]))]


if __name__ == "__main__":
    count = 0
    typedict = {}
    saving("/data/newmitx/MITx_6_00_2x_7__1T2017/log_data/vismooc",
           FILE_OUTPUT,
           concatenating(
               mapping(
                   concatenating(
                       mapping(
                           loading(
                               "/data/newmitx/MITx_6_00_2x_7__1T2017/log_data/newmitx",
                               FILE_INPUT
                           ),
                           MAP_DICT
                       )
                   ),
                   POST_PROCESS_MAP_DICT
               )
           )
           )
    print(typedict)
    print(count)
