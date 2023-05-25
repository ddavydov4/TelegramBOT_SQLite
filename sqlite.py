import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY, name TEXT, email TEXT)")

    db.commit()


async def create_profile(user_id):
    user = cur.execute("SELECT 1 FROM users WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?, ?, ?)", (user_id, '', ''))
        db.commit()


async def edit_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE users SET name = '{}', email = '{}' WHERE user_id == '{}'".format(
            data['name'], data['email'], user_id))
        db.commit()


async def get_all_users():
    users = cur.execute("SELECT * FROM users").fetchall()
    user_list = []
    for user in users:
        user_dict = {'id': user[0], 'name': user[1], 'email': user[2]}
        user_list.append(user_dict)
    return user_list


async def delete_user_by_id(user_id, cur):
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    if cur.rowcount > 0:
        return True
    else:
        return False