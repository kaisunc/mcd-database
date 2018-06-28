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
import os    
sound_path = u"//192.168.163.63/audio/MCD Database/Splice/Delectable House"
def find_files( files, dirs=[], extensions=[]):
    new_dirs = []
    for d in dirs:
        try:
            new_dirs += [ os.path.join(d, f) for f in os.listdir(d) ]
        except OSError:
            if os.path.splitext(d)[1] in extensions:
                files.append(d)

    if new_dirs:
        find_files(files, new_dirs, extensions )
    else:
        return
files = []        
find_files(files, dirs=sound_path, extensions=[".wav"])        

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
sound_path = u"d:/Hybrid Library"
dirs = os.listdir(sound_path)
this_tag = dirs[5]
this_path = "%s/%s" % (sound_path, this_tag)

q = queue.Queue()
for d in dirs[6:10]:
    this_path = "%s/%s" % (sound_path, d)
    for root, dirs, files in os.walk(this_path, topdown=False):
        files = [ fi for fi in files if fi.endswith((".mp3",".wav",".ogg")) ]
        for name in files:
            q.put([name, root])
        #file_path = (os.path.join(root, name))
#%%
while q.qsize() != 0:
    print q.get()
#%%            
def addFile(q):
    while q.qsize() != 0:
        name, root = q.get()
        #print name
        tags = root.replace(sound_path,"")[1:].split("\\")
        tags.append(u"Pro Sound Effects")
        tags.append(u"PSE")
        tags.append(u"hybrid library")    
        file_path = (os.path.join(root, name))
        m = Media(name=name, category=6, assigned=1, tags=",".join(tags), thumbnail="")
        db.session.add(m)
        db.session.commit() 
        mid = m.id
        upload_path = r"//mcd-one/database/mcd_db/sfx/%08d" % int(mid)            
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
