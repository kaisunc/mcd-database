# -*- coding: utf-8 -*-
"""
Created on Thu May 24 10:02:10 2018

@author: julio
"""


from PIL import Image
import iptcinfo
import os, shutil

tag_name_to_id = dict([ (v, k) for k, v in ExifTags.TAGS.items() ])

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

def getTags(im):
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


filename  = "75187846_xxl.jpg"
image_path = r"//mcd-one/web_project/(4)素材區/素材-圖庫/1_視訊".decode("utf8")
#full_path = image_path + "/" + filename

image_list_temp = os.listdir(image_path)
image_list = []
for image in image_list_temp:
    if 'jpg' in image and "_xxl" in image and "." not in image[0]:
        image_list.append(image)

for image in image_list[0:10]:        
    full_path = "%s/%s" % (image_path, image)
    tags = ""
    if os.path.isfile(full_path):
        im = Image.open(full_path)
        try:
            tags = getTags(im)        
        except:
            exif = convert_exif_to_dict(im._getexif())
            tags = exif['XPKeywords'].split(";")
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
os.path.isfile(full_path)
image = Image.open(full_path)


size = (120, 120)

image.thumbnail(size, Image.ANTIALIAS)
image.save("c:/sthpw/thumb.jpg")

#%%



for x in range(0,100):
    name = paths[random.randint(0, len(paths) - 1)]
    tag = randomTag(random.randint(2,10))
    print randomTag(random.randint(2,10))
    print tag
    category=cat_ids[random.randint(0,len(cat_ids) -1)]
    assigned=user_ids[random.randint(0,len(user_ids) - 1)]
    m = Media(name="asdf", category=category, assigned=assigned, tags=tag, thumbnail="")
    #print name, category, tag
    db.session.add(m)
#db.session.rollback()
#db.session.flush()
    print tag
db.session.commit() 


            for thumb in thumbs:
                if thumb['name'] == item_name:
                    # t = decode_base64(thumb['thumb'])
                    t = thumb['thumb'].split(",")[-1]
                    thumb_path = "%s/%s/%08d" % (base_path, item_category['label'], item_id)
                    if os.path.isdir(thumb_path) is False:
                        os.makedirs(thumb_path)

                    im = Image.open(BytesIO(base64.b64decode(t)))
                    im = im.convert("RGB")
                    im.save(thumb_path + "/thumb.jpg", "JPEG", quality=80, optimize=True)


#%%
for segment, content in im.applist:
    marker, body = content.split('\x00', 1)
    if segment == 'APP1' and marker == 'http://ns.adobe.com/xap/1.0/':
        # parse the XML string with any method you like
        print body
        
front= "<MicrosoftPhoto:LastKeywordXMP><rdf:Bag>"
back = "</rdf:Bag></MicrosoftPhoto:LastKeywordXMP>"

if front in body:
    print front
f = body.index(front) + len(front)
b = body.index(back)

body1 =body[f:b]
mid = "</rdf:li><rdf:li>"
ff = "<rdf:li>"
bb = "</rdf:li>"
body2 = body1.replace(mid, ",").replace(ff, "").replace(bb, "").split(",")

body2
