# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:37:44 2018

@author: julio
"""

"192.168.160.24"


model = Media
fields, columns, columnDefs = getFields(model)
search=u"行動裝置 OR 城市 OR 錢 OR 背景 OR 其他"
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
        if tag == u"多人":
            pass
        else:
            new_tags.append(tag)
    #tags = tags.replace(",多人", "")
    item.tags = ",".join(new_tags)
db.session.commit()
    


db.session.flush()
now = db.func.now()
for k, v in data.iteritems():
    setattr(update, k, v)
    if 'timestamp' in cols:
        update.timestamp = now
db.session.commit()
update = model.query.filter_by(id=pid).first()
#dt_data = json.dumps(update.dt_data_row())

dt_data = json.dumps(update.as_dict1(fields))
emit('update_response', {'data': dt_data}, broadcast=False)