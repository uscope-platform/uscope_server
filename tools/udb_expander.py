import tarfile, json

tar = tarfile.open("../uDB", 'r:xz')

for i in tar.getmembers():
    with open(i.name,'w') as f:
        json.dump(json.load(tar.extractfile(i)), f, indent=4)

tar.close()