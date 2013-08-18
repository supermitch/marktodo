import os

def argparse():
    """ Returns an arguments namespace. """
    import argparse

    parser = argparse.ArgumentParser(description='Markdown Todo List generator')

    parser.add_argument('-f',
                    help='folder to search')
    parser.add_argument('-r', action='store_false', default=True,
                    help='recursive folder search')
    parser.add_argument('-o', metavar='out-file', default='todo.mkd',
                    type=argparse.FileType('wt'),
                    help='output file (default is todo.mkd)')
    parser.add_argument('-e', nargs='*', dest='ext',
                    help='file extensions to search')

    args = parser.parse_args()

    # Clean off any leading * if present, e.g. *.py should be .py
    args.ext = [ext.lstrip('*') for ext in args.ext]

    if not os.path.isdir(args.f):
        sys.exit('Input folder not found: {}'.format(args.f))

    return args


def find_files(folder, extensions, recursive):
    """ Returns a list of files returned from os.walk if the files have
    one of a list of valid extensions. """
    valid_files = []
    for root, subdir, files in os.walk(folder):
        for f_name in files:
            if os.path.splitext(f_name)[1] in extensions:
                valid_files.append(os.path.join(root, f_name))
        if not recursive:
            break
    return valid_files


def chop_line(line, limit=79):
    """ Chops a line off either at the limit, or at nearly the last space.
    Adds '...' if the line was chopped.
    """
    if len(line) > limit:
        last_space = line.rfind(' ')
        if last_space > limit - int(len(line) * 0.1):
            break_point = last_space
        else:
            break_point = limit
        return line[:break_point-3] + '...'
    else:
        return line
            
def clean_line(raw):
    """ Cleans up a line to make it presentable as a TODO item.
    Strips whitespace, chops to length limit, and removes comment symbol.
    """
    clean = raw.strip()
    clean = chop_line(clean)
    # TODO: Remove comment symbols
    return clean


def find_todos(filename):
    """ Finds all the TODO stings in a given file.
    Returns a tuple containing filename, line number, and the line itself.
    """
    if not os.path.isfile(filename):
        print('Warning, could not find file: {}'.format(filename))
        return None

    todos = []
    with open(filename, 'r') as f:
        for line_no, raw_line in enumerate(f, start=1):
            if raw_line.find('TODO') != -1:
                clean = clean_line(raw_line)
                todos.append((filename, line_no, raw_line, clean))
    return todos


def print_todos(args, todos):
    """ Does the printing of todo list to markdown file. """
    from datetime import datetime

    out_file = args.o

    file_count = len(todos)
    total_count = 0
    for file_todos in todos:
        total_count += len(file_todos) 
    
    with out_file as f:
        f.write('# Markdown TODO list\n\n')
        f.write('Searching folder: **{}**  \n'.format(args.f))
        f.write('Recursive search: **{}**  \n'.format(args.r))
        f.write('Extensions: **{}**  \n'.format('**, **'.join(args.ext)))
        f.write('  \n')
        f.write('Found **{0}** items in **{1}** files\n'
                    ''.format(total_count, file_count))
        f.write('- - -\n')
        f.write('\n')
        for file_todos in todos:
            file_name = file_todos[0][0]
            f.write('#### {}\n'.format(file_name))
            for f_name, line_no, raw_line, clean in file_todos:
                f.write('    {0}: {1}\n'.format(line_no, clean))

            f.write('\n')
        f.write('- - -\n')
        f.write('*Generated {}*'.format(str(datetime.now())))


def main():
    args = argparse()
    
    file_list = find_files(args.f, args.ext, args.r)

    todos = []
    for f_name in file_list:
        file_todos = find_todos(f_name)
        if file_todos:
            todos.append(file_todos)
    
    print_todos(args, todos)


if __name__=='__main__':
    main()
