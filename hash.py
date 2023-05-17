from hashids import Hashids


hasher = Hashids('sdklfjdlskfjlkdsjflkj')

print(hasher.encode('this is crazy'))
