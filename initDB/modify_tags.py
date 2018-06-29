# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:37:44 2018

@author: julio
"""

"192.168.160.24"


model = Media
fields, columns, columnDefs = getFields(model)
#search=u"简"
search=u"簡"
items = model.query.whoosh_search(search).all()
len(items)

for i in items:
    print i.tags
#%%
cols = update[0].__table__.columns.keys()


for item in items:
    tags = item.tags.split(",")
    new_tags = []
    for tag in tags:
        if tag == u"簡":
            pass
        else:
            new_tags.append(tag)
    new_tags.append(u"簡")
    item.tags = ",".join(new_tags)
db.session.commit()
    
db.session.rollback()

db.session.flush()
now = db.func.now()
for k, v in data.iteritems():
    setattr(update, k, v)
#dt_data = json.dumps(update.dt_data_row())
    if 'timestamp' in cols:
        update.timestamp = now
db.session.commit()
update = model.query.filter_by(id=pid).first()

dt_data = json.dumps(update.as_dict1(fields))
emit('update_response', {'data': dt_data}, broadcast=False)
print u"中文".encode("utf8")
r"中文"

#%%
items = Media.query.filter(Media.id <= 27845).filter(Media.id >= 27784)
for item in items:
    item.tags = item.tags.replace("Aircraft - Jets","") + ",Aircraft - Jets"
    print item.tags
db.session.commit()    




#%%
Media.query.filter(Media.id > 28355).delete()
db.session.commit()

    