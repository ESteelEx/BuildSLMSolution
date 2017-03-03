import os, shutil
import xml.etree.ElementTree as ET
from os import walk


# _DEV_SOURCE = r'F:\10012017b\dev\\'
_DEV_SOURCE = r'D:\Lars_dev\dev\\'
_PATH_ADDITIVE_TARGET = r'D:\mwAdditiveSLMRelease\\'

_PATH_ADDITIVE_SOURCE = _DEV_SOURCE + r'5axis\mwAdditive\\'
_REMOVE_STR = 'AdditiveUtils'
_FILENAME_SLM_SOLUTION_SOURCE = _PATH_ADDITIVE_SOURCE + r'SLMTestApp\AdditiveSLMTestApp.sln'
_FILENAME_SLM_SOLUTION_TARGET = _PATH_ADDITIVE_TARGET + r'SLMTestApp\AdditiveSLMTestApp.sln'
_PATH_UTILS = _PATH_ADDITIVE_TARGET + r'5axis\mwAdditive\Utils\\'
_PATH_BUILD_4ALL = _DEV_SOURCE + r'5axis\buildAll4customer\\'
_FILENAME_BUILD_4ALL = _PATH_BUILD_4ALL + r'buildAll4customer.bat'
_PATH_HEADER_SOURCE = _DEV_SOURCE + r'5axis\customer\5axutil\\'
_PATH_HEADER_TARGET = _PATH_ADDITIVE_TARGET + r'Headers\\'
_PATH_BOOST_SOURCE = _DEV_SOURCE + r'libraries\boost\\'
_PATH_BOOST_TARGET = _PATH_ADDITIVE_TARGET + r'boost\\'
_FILE_SHARED_PROJ = _PATH_ADDITIVE_TARGET + 'SharedProperties.props'
_PATH_VISUALIZER_SOURCE = _DEV_SOURCE + 'libraries\DebugTools\include\\'

_PATH_REMOVE_FDM = ['FDMParams', '', '']
_SOLUTION_COPY_LIST = ['Core', 'SLMCore', 'SLMLib', 'SLMWrapper', 'Utils', 'SLMTestApp', 'SharedProperties.props']
_ADDITIONAL_HEADER_LIST = [r'Visualizer.hpp']


# ----------------------------------------------------------------------------------------------------------------------
def read_file(file):
    fid = open(file, 'r')
    content = fid.readlines()

    return content


# ----------------------------------------------------------------------------------------------------------------------
def run_file(command):
    os.system(command)


# ----------------------------------------------------------------------------------------------------------------------
def find_all(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


# ----------------------------------------------------------------------------------------------------------------------
def find_ProjectSection(file_content, str_begin, str_end):
    line_list_start_end = []
    line_pos = 0
    while len(file_content) > line_pos:
        line = file_content[line_pos]
        line_pos += 1
        line_begin = line.find(str_begin)
        if line_begin != -1:
            if line.strip().find(str_begin) == 0:
                line_list_start_end.append(line_pos)
                for line in file_content[line_pos:]:
                    line_pos += 1
                    line_end = line.find(str_end)
                    if line_end != -1:
                        if line_begin == line_end:
                            line_list_start_end.append(line_pos)
                            break

    return line_list_start_end


# ----------------------------------------------------------------------------------------------------------------------
def remove_dependencies(file_content, section_start, section_end):
    with open(_FILENAME_SLM_SOLUTION_TARGET) as fid:
        for line in fid:
            if line.find(_REMOVE_STR) != -1:
                pos_open = find_all(line, '{')
                pos_close = find_all(line, '}')
                build_ID = line[pos_open[-1] + 1:pos_close[-1]]

    sections_start_end_line = find_ProjectSection(file_content, section_start, section_end)

    line_to_remove = []
    for i in range(0, len(sections_start_end_line), 2):
        for ii in range(sections_start_end_line[i], sections_start_end_line[i + 1] - 1):
            line = file_content[ii]
            if line.find(build_ID) != -1:
                if sections_start_end_line[i + 1] - sections_start_end_line[i] < 3:
                    line_to_remove.append(ii)
                    line_to_remove.append(ii + 1)
                    line_to_remove.append(ii + 2)
                else:
                    line_to_remove.append(ii + 1)

    fid.close()

    fid = open(_FILENAME_SLM_SOLUTION_TARGET, 'w')
    for line, i in zip(file_content, range(len(file_content))):
        if i + 1 not in line_to_remove:
            fid.write(line)


# ----------------------------------------------------------------------------------------------------------------------
def get_file_list(path):
    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        f.extend(filenames)
        break

    return f


# ----------------------------------------------------------------------------------------------------------------------
def remove_files_from_folder(path, file_list, type='*.*'):
    try:
        for file in file_list:
            if type != '*.*':
                if file[-3:] == type:
                    print 'Removing file: ' + file
                    os.remove(path + file)
            else:
                print 'Removing file: ' + file
                os.remove(path + file)

    except:
        print 'Could not remove files.'

# ----------------------------------------------------------------------------------------------------------------------
def copy_files_by_list(file_list, dest_path, type='list', source_path=''):

    for entry in file_list:
        source_path_plus = str(source_path + entry).decode('string_escape').replace('\\', '\\\\')
        dest_path_plus = str(dest_path + entry).decode('string_escape').replace('\\', '\\\\')

        if os.path.isdir(source_path_plus):
            shutil.copytree(source_path_plus, dest_path_plus)
        elif os.path.isfile(source_path_plus):
            shutil.copy(source_path_plus, dest_path_plus)
        else:
            print 'File/Path not found: ' + source_path_plus


# ----------------------------------------------------------------------------------------------------------------------
def copy_files(file_list, dest_path, type='*.*', source_path=''):
    try:
        os.mkdir(dest_path)
    except:
        print 'Folder already exists or could not be created.'

    for file in file_list:
        if type != '*.*':
            if file[-3:] == type:
                # print 'Copying file: ' + file
                shutil.copy(source_path + file, dest_path + file)
        else:
            # print 'Copying file: ' + file
            shutil.copy(source_path + file, dest_path + file)


# ----------------------------------------------------------------------------------------------------------------------
def proof_folder(path, user_permission=True):

    if os.path.isdir(path):
        if user_permission:
            answer = raw_input('Folder already exists: ' + _PATH_ADDITIVE_TARGET + '.\nDelete folder? (Y/N)')
        else:
            answer = 'Y'

        if answer == 'Y':
            try:
                print 'REMOVING FOLDER: ' + path
                shutil.rmtree(_PATH_ADDITIVE_TARGET)
            except:
                print 'COULD NOT DELETE FOLDER: ' + path


# ----------------------------------------------------------------------------------------------------------------------
def remove_namespaces(tree):
    import re

    for el in tree.getiterator():
        match = re.match("^(?:\{.*?\})?(.*)$", el.tag)
        if match:
            el.tag = match.group(1)

    return tree

# ----------------------------------------------------------------------------------------------------------------------
def mod_XML(file, str1, str2, rep_str3):

    tree = ET.parse(file)
    tree = remove_namespaces(tree)
    root = tree.getroot()

    rep_str3 = rep_str3.decode('string_escape')
    if rep_str3[-1] == '\\':
        rep_str3 = rep_str3[:-1]
    rep_str3 = rep_str3.replace('\\', '\\\\')

    for child in root:
        if child.tag.find(str1) != -1:
            for child_02 in child.getchildren():
                if child_02.tag.find(str2) != -1:
                    child_02.text = rep_str3

    tree = ET.ElementTree(root)
    tree.write(file)


# ----------------------------------------------------------------------------------------------------------------------
def main():
    command = r'BuildConsole ' + \
              _FILENAME_SLM_SOLUTION_SOURCE + \
              r' /build /cfg="Release|x64" /prj=AdditiveUtilsExtern /openmonitor'

    print 'BUILDING SOLUTION WITH INCREDIBUILD ...'
    run_file(command)
    print 'DONE'

    print 'INIT COPY PROCESS'
    try:
        proof_folder(_PATH_ADDITIVE_TARGET, user_permission=False)
        print 'COPYING ADDITIVE FOLDER'
        copy_files_by_list(_SOLUTION_COPY_LIST, _PATH_ADDITIVE_TARGET, type='list', source_path=_PATH_ADDITIVE_SOURCE)
    except:
        print 'FAIL. COULD NOT COPY FILES.'
    print 'DONE'

    file_content = read_file(_FILENAME_SLM_SOLUTION_TARGET)
    print 'REMOVING ADDUTILS DEPENDENCIES FROM SOLUTION FILE'
    remove_dependencies(file_content, 'ProjectSection', 'EndProjectSection')
    remove_dependencies(file_content, 'GlobalSection', 'EndGlobalSection')
    print 'DONE'

    file_list = get_file_list(_PATH_UTILS)
    print 'REMOVING CPP FILES FROM UTILS'
    remove_files_from_folder(_PATH_UTILS, file_list, type='cpp')
    print 'DONE'

    command = _FILENAME_BUILD_4ALL
    working_dir = os.getcwd()
    print 'CHANGING WORKING DIR'
    os.chdir(_PATH_BUILD_4ALL)
    print 'RUNNING BUILD 4ALL'
    run_file(command)
    print 'CHANGING WORKING DIR'
    os.chdir(working_dir)
    print 'DONE'

    file_list = get_file_list(_PATH_HEADER_SOURCE)
    print 'INIT COPY PROCESS'
    proof_folder(_PATH_HEADER_TARGET)
    print 'COPYING HEADER FILES'
    copy_files(file_list, _PATH_HEADER_TARGET, type='hpp', source_path=_PATH_HEADER_SOURCE)
    print 'COPYING ADDITIONAL HEADER FILES'
    copy_files_by_list(_ADDITIONAL_HEADER_LIST, _PATH_HEADER_TARGET, type='list', source_path=_PATH_VISUALIZER_SOURCE)
    print 'DONE'

    print 'INIT COPY PROCESS'
    try:
        proof_folder(_PATH_BOOST_TARGET)
        print 'COPYING BOOST FOLDER'
        shutil.copytree(_PATH_BOOST_SOURCE, _PATH_BOOST_TARGET)
    except:
        print 'FAIL. COULD NOT COPY ALL FILES.'

    print 'DONE'

    print 'ADAPTING XML FILE'
    mod_XML(_FILE_SHARED_PROJ, 'PropertyGroup', 'RLSCUT_INCLUDE', _PATH_HEADER_TARGET)
    mod_XML(_FILE_SHARED_PROJ, 'PropertyGroup', 'BOOST_INCLUDE', _PATH_BOOST_TARGET)
    mod_XML(_FILE_SHARED_PROJ, 'PropertyGroup', 'VISUALIZER_INCLUDE', _PATH_HEADER_TARGET)
    print 'DONE'

    print '-------------------------------------------------------------------------------'
    print 'SCRIPT DONE'


if __name__ == '__main__':
    main()