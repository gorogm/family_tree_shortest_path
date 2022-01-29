from gedcom.element.individual import IndividualElement
from graphviz import Digraph

def find(root_child_elements, family_name, given_name, birthyear=None):
    for element in root_child_elements:
        if isinstance(element, IndividualElement):
            (first, last) = element.get_name()
            if family_name in last and given_name in first:
                if birthyear is None:
                    return element
                # if element.get_birth_year() == -1 or element.get_birth_year() == birthyear:
                if element.get_birth_year() == birthyear:
                    return element
    return None
                    
def toString(p):
    string = p.get_name()[1] + ' ' + p.get_name()[0]
    birthyear = p.get_birth_year()
    deathyear = p.get_death_year()

    return string + ' (' + (str(birthyear) if birthyear > 0 else '') + ' - ' + (str(deathyear) if deathyear > 0 else '') + ')'

def getRelation(gedcom_parser, current, new_current):
    if new_current in gedcom_parser.get_parents(current):
        if current.get_gender() == 'M':
            return ' son of '
        elif current.get_gender() == 'F':
            return ' daughter of '
        else:
            return ' child of '
    elif current in gedcom_parser.get_parents(new_current):
        if current.get_gender() == 'M':
            return ' father of '
        elif current.get_gender() == 'F':
            return ' mother of '
        else:
            return ' parent of '
    else:
        return ' spouse of '

def getRelationDirection(gedcom_parser, current, new_current):
    if new_current in gedcom_parser.get_parents(current):
        return 1
    elif current in gedcom_parser.get_parents(new_current):
        return -1
    else:
        return 0

def findConnection(gedcom_parser, p1, p2):
    visited = set([p1])
    leaves = set([p1])
    jumps = dict()
    while len(leaves) > 0:
        leaves_this_round = leaves.copy()
        leaves = set()
        for l in leaves_this_round:
            families = gedcom_parser.get_families(l)
            for f in families:
                for p in gedcom_parser.get_family_members(f):
                    if p not in visited:
                        jumps[p] = l
                        if p == p2:
                            print('found')
                            return jumps
                        visited.add(p)
                        leaves.add(p)
            for p in gedcom_parser.get_parents(l):
                if p not in visited:
                    jumps[p] = l
                    if p == p2:
                        print('found')
                        return jumps
                    visited.add(p)
                    leaves.add(p)
    return jumps

def drawJumps(gedcom_parser, target, jumps):
    f = Digraph('connection', format='jpg', encoding='utf8', filename='connection', node_attr={'style': 'filled'},  graph_attr={"concentrate": "true", "splines":"ortho"})
    f.attr('node', shape='box')

    current = target
    i = -1
    while current in jumps:
        i+=1
        new_current = jumps[current]
        f.node(str(i), label = toString(current), _attributes={'color':'lightpink' if current.get_gender()=='F' else 'lightblue'if current.get_gender()=='M' else 'lightgray'})
        if getRelationDirection(gedcom_parser, current, new_current)  == 1:
            f.edge(str(i+1), str(i), label='')
        if getRelationDirection(gedcom_parser, current, new_current)  == -1:
            f.edge(str(i), str(i+1), label='')
        if getRelationDirection(gedcom_parser, current, new_current)  == 0:
            f.edge(str(i), str(i+1), label='', constraint='False', dir = 'none')
        current = new_current

    i+=1
    f.node(str(i), label = toString(current), _attributes={'color':'lightpink' if current.get_gender()=='F' else 'lightblue'if current.get_gender()=='M' else 'lightgray'})

    return f