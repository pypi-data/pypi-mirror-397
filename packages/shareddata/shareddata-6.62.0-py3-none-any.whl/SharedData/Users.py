import os

def get_user_table(shdata):
    return shdata.table(
        'Symbols', 'D1', 'AUTH', 'USERS', 
        user='SharedData',
        names=['symbol'], 
        formats=['|S256'],
        is_schemaless=True, 
        size=1e6
    )

def get_master_user(shdata):
    user_table = get_user_table(shdata)
    master_user = user_table.loc['master']
    if len(master_user) == 0:
        # create master user with generic token
        master_user = {
            'symbol': 'master',
            'token': os.environ['SHAREDDATA_TOKEN'],
            'permissions': '*'
        }
        user_table.upsert(master_user)

    master_user = user_table.loc['master'][0]
    return master_user