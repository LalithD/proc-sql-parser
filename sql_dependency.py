import re

def remove_comments(string):
    'Remove comments (those that are encapsulated between "/*" and "*/")'
    return re.sub(r'/\*.*?\*/', '', string) # this is /* --- */ with minimal matching

def collapse_spaces(string):
    'Replace all consecutive whitespace with a single space'
    return re.sub(r'\s+', ' ', string)

def get_query_list(string):
    'Split program into SQL queries and return as list'
    string = remove_comments(string)
    string = collapse_spaces(string)
    string = string.strip() # remove leading and trailing whitespace
    string = string.lower() # lowercase only for easy parsing
    # TODO: Look for "proc sql;" and "quit;" and take text in between
    arr = re.findall('proc sql;.*?quit;', string)
    return [i[len('proc sql;'):-len('quit;')] for i in arr]

def parse_table_sql(query):
    'Return created table name'
    cleaned_query = query.lower() # assume query is partly cleaned already
    create_table_location = cleaned_query.index('create table ')
    begin_new_table_name = create_table_location + len('create table ')
    new_string = query[begin_new_table_name:]
    end_new_table_name = new_string.index(' ')
    new_table_name = query[begin_new_table_name:begin_new_table_name + end_new_table_name]
    return new_table_name

def parse_table_sql2(query):
    'Return created table name2'
    cleaned_query = query.lower()
    re.find('create\s*table\s*.*?', cleaned_query)

def parse_from_sql(query):
    'Return list of tables used in table creation (in FROM or JOIN clauses)'
    cleaned_query = query.lower()
    from_table_location1 = cleaned_query.index(' from ')
    begin_from_table_name1 = from_table_location1 + len(' from ')
    new_string = query[begin_from_table_name1:]
    end_from_table_name1 = new_string.index(' ')
    table_name1 = query[begin_from_table_name1:begin_from_table_name1 + end_from_table_name1]
    # TODO: If there is a comma after "FROM <table1>", then there is at least one table inner-joined
    # TODO: Check for tables from JOINS
    return [table_name1]
    
def get_dependency(query):
    'Print dependencies of a single query'
    new_table = parse_table_sql(query) # name of table being created
    from_tables = parse_from_sql(query) # list of from tables
    for table in from_tables:
        print('{} <- {}'.format(new_table, table))
        
def get_all_dependencies(file):
    'Print all table dependencies from a given text file'
    string = None
    with open(file, 'r') as f:
        string = f.read().replace('\n', ' ')
    query_list = get_query_list(string)
    for query in query_list:
        get_dependency(query)
        print('################################')
        
def rf(file):
    string = None
    with open(file, 'r') as f:
        string = f.read().replace('\n', ' ')
    return string            

#regex looks something like:
    
#join[space]texttexttext[ends in space or semicolon or comma]
# '\sjoin\s.*?[\s;,]'
# 'create\s*table\s*.*?'
def select_string(string):
    str_list = list(string)
    comma_locations = normal(str_list, 0, 0)
    split_list = [string[:comma_locations[0]]]
    for i in range(len(comma_locations)-1):
        split_list.append(string[comma_locations[i]+1:comma_locations[i+1]].strip())
    split_list.append(string[comma_locations[len(comma_locations)-1]:])
    return split_list

def normal(str_list, index, depth):
    if index == len(str_list):
        return []
    if depth > 0:
        parentheses(str_list, index, depth)
    if index+1 < len(str_list) and str_list[index] == '/' and str_list[index+1] == '*':
        return comment(str_list, index+2, depth)
    elif str_list[index] == '\'':
        return singlequote(str_list, index+1, depth)
    elif str_list[index] == '"':
        return doublequote(str_list, index+1, depth)
    elif str_list[index] == '(':
        return normal(str_list, index+1, depth+1)
    elif str_list[index] == ')':
        return normal(str_list, index+1, depth-1)
    elif depth == 0 and str_list[index] == ',':
        return [index] + normal(str_list, index+1, depth)
    else:
        return normal(str_list, index+1, depth)
    
def comment(str_list, index, depth):
    while index+1 < len(str_list) and not (str_list[index] == '*' and str_list[index+1] == '/'):
        index += 1
    if index+1 < len(str_list) and str_list[index] == '*' and str_list[index+1] == '/':
        return normal(str_list, index+2, depth)
    else:
        return []
    
def singlequote(str_list, index, depth):
    while index < len(str_list) and not str_list[index] == '\'':
        index += 1
    if index < len(str_list) and str_list[index] == '\'':
        return normal(str_list, index+1, depth)
    else:
        return []
    
def doublequote(str_list, index, depth):
    while index < len(str_list) and not str_list[index] == '"':
        index += 1
    if index < len(str_list) and str_list[index] == '"':
        return normal(str_list, index+1, depth)
    else:
        return []
