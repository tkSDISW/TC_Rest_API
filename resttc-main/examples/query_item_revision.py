from teamcenter.connection import get_connection, config_alias, reset_connection
from teamcenter.commands import get_command


def main():
    config_alias('DEFAULT')
    conn = get_connection()
    print(conn.session)

    #Get our saved query...
    fsq = get_command('FindSavedQuery')
    fsq.set_cmd('Item Revision...')
    
    saved_query = conn.handle(fsq)

    esq = get_command('ExecuteSavedQuery')
    esq.set_cmd(saved_query,
                ["Type"],
                ["Item Revision"],
                1)
                
    item_revs = conn.handle(esq)
    print(item_revs)

if __name__ == '__main__':
    main()