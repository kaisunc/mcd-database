# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:14:38 2018

@author: julio
"""

#%%
names = ["Velia","Heidy","Han","Takako","Odessa","Florance","Giuseppe","Remedios","Samual","Laurie","Beulah","Cathey","Rico","Stefanie","Pilar","Shaquita","Hulda","Tina","Demarcus","Phyllis","Thomasena","Vern","Dorotha","Ulrike","Delilah","Natashia","Janette","Serena","Ines","Tiffanie","Lamar","Lakendra","Herma","Trina","Carmon","Kathey","Byron","Suellen","Christene","Tosha","Imogene","Ethelene","Kyle","Elliott","Olene","Rex","Ruben","Kathrine","Lakenya","Melissa"]

#%%
for x in range(0,50):
    user = User(name=names[x])
    db.session.add(user)
    
db.session.commit()

user = User(name, name_chn)

#%%
category = ["fonts", "software", "images", "effects", "plugins/brushes", "sound", "tutorials", "web_templates"]
for x in category:
    c = Category(name=x)
    db.session.add(c)

db.session.commit()    

Category.query.all()
#%%
import random
names = ["Velia","Heidy","Han","Takako","Odessa","Florance","Giuseppe","Remedios","Samual","Laurie","Beulah","Cathey","Rico","Stefanie","Pilar","Shaquita","Hulda","Tina","Demarcus","Phyllis","Thomasena","Vern","Dorotha","Ulrike","Delilah","Natashia","Janette","Serena","Ines","Tiffanie","Lamar","Lakendra","Herma","Trina","Carmon","Kathey","Byron","Suellen","Christene","Tosha","Imogene","Ethelene","Kyle","Elliott","Olene","Rex","Ruben","Kathrine","Lakenya","Melissa"]
category = ["fonts", "software", "images", "effects", "plugins/brushes", "sound", "tutorials", "web_templates"]

for name in names:
    c = Media(name=name, category=random.randrange(1,len(category) + 1))
    db.session.add(c)    
#db.session.rollback()
db.session.flush()
db.session.commit()    
