
def xml_to_txt(xml_file, txt_file):

    txt_file_handle = open(txt_file, 'w')
    for each_line in open(xml_file):
        each_line = each_line.strip()
        if (each_line.count('<') == 1) and (each_line.count('>') == 1):
            pass
        else:
            each_line = each_line.split('</')[0]
            title_str = each_line.split('>')[0][1:]
            value_str = each_line.split('>')[-1]
            if 'display_name' in title_str:
                title_str = title_str.split('display_name')[1].replace('=','').replace('"','')
            elif title_str.count('=') == 1:
                title_str = title_str.split('=')[1].replace('"','')
            elif title_str.count('=') == 0:
                title_str = title_str
            elif 'is_primary' in title_str:
                title_str = title_str.split('is_primary')[0].split('=')[1].replace('"','')
            txt_file_handle.write('%s\t%s\n' % (title_str, value_str))
    txt_file_handle.close()


xml_file = '/Users/songweizhi/Desktop/demo/biosample_wd/SAMEA13322663.xml'
txt_file = '/Users/songweizhi/Desktop/demo/biosample_wd/SAMEA13322663.txt'


import pandas as pd

df = pd.read_xml(xml_file)
print(df)
# df.to_csv(txt_file, index=False)