tree = {'name':'1',
        'children': [{'name':'2',
                    'children': [{'name':'4',
                                'children': []}]
                                },
                    {'name':'3',
                    'children': []}
                    ]}

def par_ret(t, node_name):
    print(t['name'])
    if t['name'] == node_name:
        return t["name"]
    elif t['children']:
        for child in t['children']:
            return par_ret(child, node_name)

def par(t, node_name):
    print(t['name'])
    if t['name'] == node_name:
        return t["name"]
    elif t['children']:
        for child in t['children']:
            par(child, node_name)

par_ret(tree, '3')
print("---------")
par(tree, '3')
