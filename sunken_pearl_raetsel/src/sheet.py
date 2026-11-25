import sys
from PIL import Image
d='/home/user/Stories/sunken_pearl_raetsel/frames/test/preview/'
fs=sys.argv[2:]; out=sys.argv[1]
ims=[Image.open(d+f) for f in fs]
s=Image.new('RGB',(270*len(ims),480))
for i,a in enumerate(ims): s.paste(a.resize((270,480)),(i*270,0))
s.save(out)
