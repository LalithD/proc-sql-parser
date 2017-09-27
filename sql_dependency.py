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

def mod(string):
    '''
    Modes are regular reading,
    comments - anything in which can be ignored,
    parentheses (which need to be closed)
    strings (which also need to be closed)
    '''
    new_str = ''
    in_string = 0
    in_comment = 0
    for i in len(string): # go character by character
        char = string[i]
        if not in_comment:
            new_str += char
        if in_string:
            new_str += char
            if in_string == char: # 
                in_string = 0
            

#regex looks something like:
    
#join[space]texttexttext[ends in space or semicolon or comma]
# '\sjoin\s.*?[\s;,]'
# 'create\s*table\s*.*?'
