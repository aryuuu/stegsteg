from PIL import Image
import requests
import json
import os

API_URL = "https://api.kripkrip.aryuuu.ninja/api/v1"

# def vigenere_enc():

# get nth bit on a byte
def get_bit(byte, n):
    return byte >> (7-n) & 1

def bits_to_bytes(bits):
    byte_list = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        byte_list.append(int(''.join([str(bit) for bit in byte]), 2))
    return byte_list

def bytes_to_bits(byte_list):
    bits = ''
    for byte in byte_list:
        bits += bin(byte)[2:].zfill(8)
    return bits


def open_files(cover_path, filename):
    cover_image = Image.open(cover_path)
        # check if cover file format is either PNG or BMP
    if (cover_image.format != "PNG" and cover_image.format != "BMP"):
        raise Exception("Cover file format must be PNG or BMP")

    # check if file and some metadata fit in the cover file
    width, height = cover_image.size
    filesize = os.path.getsize(filename)

    if (filesize * 8 <= width * height * 3 + 1):
        file = open(filename, 'rb')
        return cover_image, bytes_to_bits(file.read())
    else:
        raise Exception("File %s too large for %s" % (filename, cover_path))

def hide_lsb(cover_name, filename, save_as = "", key = "", mode = "SEQUENTIAL"):
    try:
        cover_image, file = open_files(cover_name, filename)
        print("files loaded")
        if (key):
            req = requests.post(
                API_URL+'/extended-vigenere/enc',
                data = {
                    'plain': file,
                    'key': key
                }
            )
            print(req.text)
            res = json.loads(req.text)
            file = res['message']

        width, height = cover_image.size

        i = 0
        is_first_bit_set = False
        for x in range(0, width):
            for y in range(0, height):
                pixel = list(cover_image.getpixel((x, y)))
                for n in range(3):
                    if (i < len(file)):
                        if (not is_first_bit_set):
                            pixel[n] = pixel[n] & ~1 | (0 if mode == "SEQUENTIAL" else 1)
                            is_first_bit_set = True
                        else:    
                            pixel[n] = pixel[n] & ~1 | int(file[i])
                            i += 1
                cover_image.putpixel((x, y), tuple(pixel))
        cover_image.save("steg-"+cover_name, cover_image.format)


    except Exception as e:
        print(e)

def extract_lsb(cover_name):
    cover_image = Image.open(cover_name)
    width, height = cover_image.size

    is_first_bit_get = False
    is_sequential = True
    extracted_bin = []

    for x in range(width):
        for y in range(height):
            pixel = list(cover_image.getpixel((x, y)))
            for n in range(3):
                if (not is_first_bit_get):
                    print('first bit acquired')
                    is_first_bit_get = True
                    is_sequential = (pixel[n]&1) == 0
                else:
                    extracted_bin.append(pixel[n]&1)

    extracted_file = open('extracted-file', 'wb')
    extracted_file.write(bytearray(bits_to_bytes(extracted_bin)))

if __name__ == "__main__":
    cover_name = "virginvschad.png"
    filename = "bigchungus.png"

    # hide_lsb(cover_name, filename)

    steg_cover_name = "steg-virginvschad.png"
    extract_lsb(steg_cover_name)
