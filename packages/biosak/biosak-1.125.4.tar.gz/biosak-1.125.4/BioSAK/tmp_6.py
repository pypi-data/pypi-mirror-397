import os
import glob


def sep_path_basename_ext(file_in):

    f_path, f_name = os.path.split(file_in)
    if f_path == '':
        f_path = '.'
    f_base, f_ext = os.path.splitext(f_name)
    f_ext = f_ext[1:]

    return f_name, f_path, f_base, f_ext


def efetch_op_to_dict(efetch_op_txt):

    metadata_dict = dict()
    for each_line in open(efetch_op_txt):
        each_line = each_line.strip()
        if not each_line.endswith(':'):
            if each_line.startswith('/'):
                each_line = each_line[1:]
                each_line_split = each_line.split('=')
                attribute_name = each_line_split[0]
                attribute_value = each_line_split[1][1:-1]
                metadata_dict[attribute_name] = attribute_value
            elif each_line.startswith('Identifiers: '):
                each_line = each_line[len('Identifiers: '):]
                each_line_split = each_line.split(';')
                for each_identifier in each_line_split:
                    each_identifier = each_identifier.strip()
                    each_identifier_split = each_identifier.split(': ')
                    metadata_dict[each_identifier_split[0]] = each_identifier_split[1]
            elif each_line.startswith('1: '):
                desc_line = each_line[len('1: '):]
                metadata_dict['sample_description'] = desc_line
            elif each_line.startswith('Organism: '):
                desc_line = each_line[len('Organism: '):]
                metadata_dict['organism'] = desc_line
            else:
                pass

    return metadata_dict


file_dir = '/Users/songweizhi/Desktop/op_dir2/tmp'
file_ext = 'txt'
combined_metadata_txt = '/Users/songweizhi/Desktop/op_dir2/tmp.txt'

file_re = '%s/*.%s' % (file_dir, file_ext)
file_list = glob.glob(file_re)

all_attr_set = set()
metadata_dod = dict()
for each_file in file_list:
    f_name, f_path, f_base, f_ext = sep_path_basename_ext(each_file)
    current_metadata_dict = efetch_op_to_dict(each_file)
    for i in current_metadata_dict:
        all_attr_set.add(i)
    metadata_dod[f_base] = current_metadata_dict

all_attr_list_sorted = sorted(list(all_attr_set))

combined_metadata_txt_handle = open(combined_metadata_txt, 'w')
combined_metadata_txt_handle.write('Biosample\t%s\n' % ('\t'.join(all_attr_list_sorted)))
for each_biosample in sorted(list(metadata_dod.keys())):
    current_biosample_attr_list = [each_biosample]
    for each_attr in all_attr_list_sorted:
        current_biosample_attr_list.append(metadata_dod[each_biosample].get(each_attr, 'na'))
    combined_metadata_txt_handle.write('\t'.join(current_biosample_attr_list) + '\n')
combined_metadata_txt_handle.close()

