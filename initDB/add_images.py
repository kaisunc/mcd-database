# -*- coding: utf-8 -*-
"""
Created on Thu May 24 10:02:10 2018

@author: julio
"""


from PIL import Image, ExifTags
import iptcinfo
import os, shutil

tag_name_to_id = dict([ (v, k) for k, v in ExifTags.TAGS.items() ])
#%%
# These I got from reading in files and matching to http://www.exiv2.org/tags.html
# You'll have to map your own if something isn't recognised
tag_name_to_id[270] = 'ImageDescription'
tag_name_to_id[306] = 'DateTime'
tag_name_to_id[256] = 'ImageWidth'
tag_name_to_id[257] = 'ImageLength'
tag_name_to_id[258] = 'BitsPerSample'
tag_name_to_id[40962] = 'PixelXDimension'
tag_name_to_id[40963] = 'PixelYDimension'
tag_name_to_id[305] = 'Software'
tag_name_to_id[37510] = 'UserComment'
tag_name_to_id[40091] = 'XPTitle'
tag_name_to_id[40092] = 'XPComment'
tag_name_to_id[40093] = 'XPAuthor'
tag_name_to_id[40094] = 'XPKeywords'
tag_name_to_id[40095] = 'XPSubject'
tag_name_to_id[40961] = 'ColorSpace' # Bit depth
tag_name_to_id[315] = 'Artist'
tag_name_to_id[33432] = 'Copyright'


def convert_exif_to_dict(exif):
    """
    This helper function converts the dictionary keys from
    IDs to strings so your code is easier to read.
    """
    data = {}

    if exif is None:
        return data

    for k,v in exif.items():
       if k in tag_name_to_id:
           data[tag_name_to_id[k]] = v
       else:
           data[k] = v

    # These fields are in UCS2/UTF-16, convert to something usable within python
    for k in ['XPTitle', 'XPComment', 'XPAuthor', 'XPKeywords', 'XPSubject']:
        if k in data:
            data[k] = data[k].decode('utf-16').rstrip('\x00')

    return data

def getTags(im, full_path):
    if im.format in ['JPEG', 'TIFF']:
        try:
            iptc = iptcinfo.IPTCInfo(full_path)
    
            image_title = iptc.data.get('object name', '') or iptc.data.get('headline', '')
            image_description = iptc.data.get('caption/abstract', '')
            image_tags = iptc.keywords
    
        except Exception, e:
            if str(e) != "No IPTC data found.":
                raise    
        return image_tags
        
def getWeirdTags(im):
    for segment, content in im.applist:
        if segment == 'APP13':
            marker, body = content.split('\x00', 1)
            front= "<rdf:Bag"
            back = "</rdf:Bag>"
        
            f = body.index(front) + len(front)
            b = body.index(back)
            
            nb = body[f:b]
            count = 1
            for c in nb:
                if c == ">":
                    break
                count = count + 1
        
            if body[f+count:b].count('<rdf:li>') == 1:
                tags = re.search("(?<=<rdf:li>)(.*)(?=<\/rdf:li>)", body[f+count:b]).group(0).replace(" ","").split(",")
                
            return tags
        else:
            return ["none"]

        
#%%
size = (120, 120)
#filename  = "67183490.jpg"
category = r"其他"
image_path = r"//mcd-one/web_project/(4)素材區/素材-圖庫/10_%s" % category
image_path = image_path.decode("utf8")


#full_path = image_path + "/" + filename

image_list_temp = os.listdir(image_path)

image_list = []
for image in image_list_temp:
    if 'jpg' in image and "." not in image[0]:
        image_list.append(image)
len(image_list)

for idx, image in enumerate(image_list):      
    print image
    full_path = "%s/%s" % (image_path, image)
    tags = ""
    if os.path.isfile(full_path):
        im = Image.open(full_path)
        try:
            tags = getTags(im, full_path)        
        except:
            try:
                exif = convert_exif_to_dict(im._getexif())
                tags = exif['XPKeywords'].split(";")
            except:
                pass
                try:
                    tags = getWeirdTags(im)
                except:
                    tags = "none"
                    print 'none'

        if len(tags) == 0:
            pass
        else:
            try:
                tags.remove('')
            except:
                pass
            tags.append(category.decode('utf8'))
            m = Media(name=image, category=4, assigned=1, tags=",".join(tags), thumbnail="")
            db.session.add(m)
            db.session.commit() 
            mid = m.id
            upload_path = r"//mcd-one/database/mcd_db/images/%08d" % int(mid)
            if not os.path.exists(upload_path):
                os.mkdir(upload_path)
            shutil.copyfile(full_path, upload_path + "/" + image)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(upload_path + "/thumb.jpg")
            print 'done'
            
            db.session.rollback()
            db.session.flush()

#%%


font_path = u"//mcd-one/web_project/(4)素材區/字型/1_中文/迷你系列"

font_list_temp = os.listdir(font_path)

font_list = []
for font in font_list_temp:
    if "." not in font[0] and "Thumbs.db" not in font:
        font_list.append(font)
len(font_list)
for idx, font in enumerate(font_list):
    print font
    full_path = "%s/%s" % (font_path, font)
    tags = [u"中文", u"迷你"]
    if u"繁" in font:
        tags.append(u"繁")
    elif u"简" in font:
        tags.append(u"简")

    m = Media(name=font, category=3, assigned=1, tags=",".join(tags), thumbnail="")
    db.session.add(m)
    db.session.commit()
    mid = m.id
    upload_path = r"//mcd-one/database/mcd_db/fonts/%08d" % int(mid)
    if not os.path.exists(upload_path):
        os.mkdir(upload_path)
    shutil.copyfile(full_path, upload_path + "/" + font)
#%%    

m = Media(name="test", category=3, assigned=1, tags="testing", thumbnail="")
db.session.add(m)
db.session.commit()