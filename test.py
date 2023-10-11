import re

slugs = []
for name in ["JefftheBabyLandShark", "M'baku", "UatutheWatcher", "Widow'sBite"]:
    slug = re.sub("[ \-]","", name)
    slug = slug.replace("the", "The")
    if "'" in slug:
        index = slug.index("'")
        slug = slug[:index]  + slug[index+1].upper() + slug[index+2:]
        slug = re.sub("[']","", slug)
    slugs.append(slug)

print(slugs)