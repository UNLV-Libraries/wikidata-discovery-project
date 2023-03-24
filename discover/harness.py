from discover import sparql, db

def test_people():
    my_json = sparql.get_wd_people()
    result = db.write_people(my_json)
    print(result)
