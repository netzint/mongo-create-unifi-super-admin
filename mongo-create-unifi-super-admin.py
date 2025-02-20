import crypt
import os
import string
from random import SystemRandom
import argparse
import pymongo

parser = argparse.ArgumentParser()
parser.add_argument('-u','--username', help='UniFi username to create')
parser.add_argument('-p','--password', help='UniFi password to create')
parser.add_argument('-e', '--email', help='UniFi email to create')
args = parser.parse_args()

randchoice = SystemRandom().choice

def sha512_crypt(password, salt=None, rounds=None):
    if salt is None:
        salt = ''.join([randchoice(string.ascii_letters + string.digits)
                        for _ in range(8)])

    prefix = '$6$'
    if rounds is not None:
        rounds = max(1000, min(999999999, rounds or 5000))
        prefix += 'rounds={0}$'.format(rounds)
    return crypt.crypt(password, prefix + salt)

if args.email is not None and args.password is not None and args.username is not None:
    print("Creating UniFi Super Admin")
    print("Connecting to MongoDB...")
    site_ids = []
    client = pymongo.MongoClient("mongodb://127.0.0.1:27117/ace")
    mdb = client.ace
    print("Inserting Admin...")
    insert_admin = mdb.admin.insert({"email" : args.email, "last_site_name" : "default", "name" : args.username, "x_shadow" : sha512_crypt(args.password)})
    db_dump = mdb.site.find()
    admin_list = mdb.admin.find()
    print("Promoting Admin to Super Admin...")
    for admin in admin_list:
        try:
            if admin["email"] == args.email:
                new_admin_id = str(admin["_id"])
        except:
            continue
    for site in db_dump:
        site_id = str(site["_id"])
        site_ids.append(site_id)
    for site_id in site_ids:
        mdb.privilege.insert({"admin_id" : new_admin_id, "site_id" : site_id, "role" : "admin", "permissions" : [ ] })
    print("Done!")

else:
    print("Error: Missing arguments. --username, --password, and --email are required.")
