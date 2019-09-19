import tarfile, json, glob

tar = tarfile.open("../uDB", 'w:xz')

for f in glob.glob('*.json'):
    tar.add(f)

tar.close()

