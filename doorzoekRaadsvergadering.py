from classes.sub import Sub
import os

Keyword = 'armoede'
files = sorted(os.listdir('json/subs'))

for filename in files:
    s = Sub(filename[0:-5])
    s.contains_keyword(Keyword)