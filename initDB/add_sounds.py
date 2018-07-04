# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 15:56:10 2018

@author: julio
"""

import os, shutil

#%%
sound_path = u"//mcd-one/audio/MCD Database/機率音效"
subdirs = os.listdir(sound_path)

for subdir in subdirs:
    #subdir = subdirs[0]
    sub_path = "%s/%s" % (sound_path, subdir)
    ssubdirs = os.listdir(sub_path)    
    for ssubdir in ssubdirs:
        ssub_path = "%s/%s" % (sub_path, ssubdir)
        #print ssub_path

        sound_files = [x for x in os.listdir(ssub_path) if "mp3" in x and "ogg" not in x and "00001" not in x]
        for sound_file in sound_files:
            tags = []
            tags.append(ssubdir.split("_")[-1])
            tags = tags + subdir.split("_")                
            m = Media(name=sound_file, category=6, assigned=1, tags=",".join(tags), thumbnail="")
            db.session.add(m)
            db.session.commit() 
            mid = m.id
            upload_path = r"//mcd-one/database/mcd_db/images/%08d" % int(mid)            
            if not os.path.exists(upload_path):
                os.mkdir(upload_path)
            full_path = "%s/%s" % (ssub_path, sound_file)
            shutil.copyfile(full_path, upload_path + "/" + sound_file)            
            print full_path

#%%        
sound_path = u"//mcd-one/audio/MCD Database/機率音效/小e公版"
sound_path = u"//192.168.163.63/audio/MCD Database/Splice/Delectable House/DR_Delectable_House/DR_DGDH_DRUMS_PACK/DGDH_LP_DRUM_PARTS/LP_DRUMS"
sound_path = u"//192.168.163.63/audio/MCD Database/Splice/Delectable House"


#%%
import os, shutil
#sound_path = u"//192.168.163.63/audio/MCD Database/Splice/Delectable House"
#sound_path = u"//192.168.163.63/audio/MCD Database/Splice"
sound_path = u"//mcd-one/audio/MCD Database/合法音樂"
#sound_path = u"d:/Hybrid Library/Acid"
for root, dirs, files in os.walk(sound_path, topdown=False):
    files = [ fi for fi in files if fi.endswith((".mp3",".wav",".ogg")) ]
    print len(files)
    for name in files:
        tags = root.replace(sound_path,"")[1:].split("\\")
        tags.append(u"Pro Sound Effects")
        tags.append(u"PSE")
        tags.append(u"hybrid library")
        file_path = (os.path.join(root, name))
        print name
        print tags
        print file_path
        print "\n"
        m = Media(name=name, category=5, assigned=1, tags=",".join(tags), thumbnail="")
        db.session.add(m)
        db.session.commit() 
        mid = m.id
        upload_path = r"//mcd-one/database/mcd_db/music/%08d" % int(mid)            
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)

        shutil.copyfile(file_path, upload_path + "/" + name)
        
       

#%%
import os, shutil
from threading import Thread
import queue

#sound_path = u"//mcd-one/audio/MCD Database/常用音效/常用音效_分類統整區"
#sound_path = u"d:/Hybrid Library"
sound_path = u"//mcd-one/2d_material/UI資料庫/Button"
dirs = os.listdir(sound_path)

q = queue.Queue()
for d in dirs:
    this_path = "%s/%s" % (sound_path, d)
    for root, dirs, files in os.walk(this_path, topdown=False):
        files = [ fi for fi in files if fi.endswith((".jpg",".psd")) ]
        for name in files:
            q.put([name, root])
        #file_path = (os.path.join(root, name))
#%%
print q.get()[1]
q.qsize()
#%%            
def addFile(q):
    while q.qsize() != 0:
        name, root = q.get()
        tags = []
        tags = root.replace(sound_path,"")[1:].split("\\")
        tags.append(u"2d")
        file_path = (os.path.join(root, name))
        m = Media(name=name, category=4, assigned=1, tags=",".join(tags), thumbnail="")
        db.session.add(m)
        db.session.commit() 
        mid = m.id
        upload_path = r"//art-server/database/mcd_db/sfx/%08d" % int(mid)            
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)

        shutil.copyfile(file_path, upload_path + "/" + name)
        print name
        print tags


for i in range(0,1):
    t = Thread(target=addFile, args=(q,))
    t.start()

#t.join()    
#%%

import sys, os, shutil
base = r"\\mcd-one\2d_material".decode("utf8")
sound_path = r"\\mcd-one\2d_material\UI資料庫\Text".decode("utf8")
dirs = [x for x in os.listdir(sound_path) if os.path.isdir(os.path.join(sound_path, x))]

for d in dirs:
    sub_path = os.path.join(sound_path, d)
    files = [f for f in os.listdir(sub_path) if f.endswith("jpg")]
    for f in files:
        tags = sub_path.replace(base,"")[1:].split(u"\\")
        tags.append("2d")
        file_path = os.path.join(sub_path, f)
        psd = f.replace(".jpg", "_work.psd")
        psd_path = os.path.join(sub_path, psd)

        print os.path.isfile(psd_path), psd_path
        print os.path.isfile(file_path), file_path

        m = Media(name=psd, category=4, assigned=1, tags=",".join(tags), thumbnail="")
        db.session.add(m)
        db.session.commit() 
        mid = m.id
        upload_path = r"//art-server/database/mcd_db/images/%08d" % int(mid)            
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)
    
        shutil.copyfile(file_path, upload_path + "/thumb.jpg")
        shutil.copyfile(psd_path, upload_path + "/" + psd)
        print psd
        print tags
    
#%%
def addFile(name, base_path, tags=[], category=4, assigned=1):
    size = 120, 120
    category_name = Category.query.filter_by(id=category).first().name
    file_path = os.path.join(base_path, name)
    m = Media(name=name, category=category, assigned=assigned, tags=",".join(tags), thumbnail="")
    db.session.add(m)
    db.session.commit() 
    mid = m.id
   
    upload_path = u"%s\\%s\\%08d" % ("\\\\art-server\\database\\mcd_db", category_name, int(mid))
    if not os.path.exists(upload_path):
        os.mkdir(upload_path)
    
    if file_path.endswith((".jpg",".png",".gif")):
        im = Image.open(file_path).convert('RGB')
        im.thumbnail(size)
        im.save(upload_path + "\\thumb.jpg", "JPEG")    

    shutil.copyfile(file_path, upload_path + "\\" + name)


#%%
import sys, os, shutil
from PIL import Image
import glob, os
ta_path = r"\\mcd-one\ta\2_Datebase\GameSources".decode("utf8")
base = r"\\mcd-one\ta\2_Datebase".decode("utf8")

dirs = [x for x in os.listdir(ta_path) if os.path.isdir(os.path.join(ta_path, x)) and x != "_Index"]
    
game_sub_dirs = ["Atlas", "Fonts", "Scene", "Symbol", "UI"]    
for d in dirs:
    game_path = os.path.join(ta_path, d)
    tags = game_path.replace(ta_path,"")[1:].split(u"\\")
    gameplay = [x for x in os.listdir(game_path) if ".mp4" in x][0]
    if len(gameplay) != 0:
        tags = tags = ["TA","GameSources"]
        addFile(gameplay, game_path, tags=tags, category=8)
    
    gamefiles = [(root, dirs, files) for (root, dirs, files) in os.walk(game_path, topdown=False) if root != game_path]
    for root, dirs, files in gamefiles:
        for f in [f for f in files if f.endswith((".jpg",".png",".gif"))]:
            #file_path = os.path.join(root, f)
            tags = root.replace(base,"")[1:].split(u"\\")
            tags.append("TA")
            addFile(f, root, tags=tags, category=4)

        

    

