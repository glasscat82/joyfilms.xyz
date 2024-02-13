## small parsing m1.joyfilms.xyz

parsing links film in TinyDB('./json/links.json')
```
# 1.
set_link()
```

get list links 
```
# 2.
for f in TinyDB('./json/links.json').all():
    p(f['fid'], f['name'], f['type'])
```

parsing detail film in TinyDB('./json/films.json')
```
# 3.
set_films()
```
