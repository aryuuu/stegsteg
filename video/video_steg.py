import cv2
from mhmovie.code import *
import math
import random
import os
import shutil

class video_steg:
    def __init__(self,filename,message='',seed=0,random_frame_state=0,random_pixel_state=0,save_as=''):
        cap = cv2.VideoCapture(filename)
        self.filename = filename
        self.num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(self.num_frames,'--',self.frame_width,'--',self.frame_height,'--',self.fps)
        # self.duration = self.num_frames/self.fps
        count = 0
        if not os.path.exists('temp'):
            os.makedirs('temp')
        ret, frame = cap.read()
        print(frame[0][0])
        while cap.isOpened():
            ret, frame = cap.read()
            cv2.imwrite('temp/%d.jpg' % count, frame)
            count += 1

            # if (count%10==0):
                # print(count/10)
            if (count >= self.num_frames-3):
                cap.release()

        self.seed = seed
        self.random_frame_state = int(random_frame_state)
        self.random_pixel_state = int(random_pixel_state)
        self.message = message
        self.save_as = save_as
        
    def steganography(self):
        if(len(self.message)*8 + 4*8 + 2 > 3*(self.num_frames-6)*self.frame_width*self.frame_height):
            return 'message is too long'
        
        msg_bit = ''.join(format(i, 'b').zfill(8) for i in bytearray(self.message, encoding='utf-8'))

        frame_byte = 3
        width_byte = 0
        height_byte = 0
        rgb_byte = 0
        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
        if (self.random_frame_state==0):
            bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + '0'
        else:
            bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + '1'

        self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
        print(self.frame[height_byte][width_byte])
        rgb_byte += 1

        if (self.random_pixel_state==0):
            bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + '0'
        else:
            bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + '1'
        
        self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
        print(self.frame[height_byte][width_byte])
        rgb_byte += 1

        msg_len_bit = bin(len(self.message))[2:].zfill(32)
        print(msg_len_bit)
        return 0
        if (self.random_frame_state==0):
            if (self.random_pixel_state==0):
                
                for i in range(32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_len_bit[i]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    # change frame if 1 pixel already steg
                    if (rgb_byte > 2):
                        rgb_byte = 0
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-6):
                            frame_byte = 0
                            height_byte += 1
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                    
                    # move to first frame and add 1 width if all frame at the same pixel already explored
                    

                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1
                
                for i in range(len(msg_bit)):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_bit[i]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    # change frame if 1 pixel already steg
                    if (rgb_byte > 2):
                        rgb_byte = 0
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-6):
                            frame_byte = 0
                            height_byte += 1
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                    
                    # move to first frame and add 1 width if all frame at the same pixel already explored
                    

                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1

            else:
                random.seed(self.seed)
                pixel_list = []
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_len_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-6):
                            frame_byte = 0 
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                    
                # insert message bit
                counter = 0
                while(counter < len(msg_bit)):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-6):
                            frame_byte = 0 
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)

        else:
            if (self.random_pixel_state==0):
                random.seed(self.seed)
                pixel_list = []
                frame_counter = self.num_frames-6
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_len_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        frame_counter -= 1
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-7)
                        if (frame_counter==0):
                            height_byte += 1
                            frame_counter = self.num_frames -6

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-7)

                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        
                    

                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1

                counter = 0
                while(counter < len(msg_bit)):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        frame_counter -= 1
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-7)
                        if (frame_counter==0):
                            height_byte += 1
                            frame_counter = self.num_frames -6

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-1)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)

                    if (height_byte >= self.frame_height):
                        height_byte = 0 
                        width_byte += 1
            else:
                random.seed(self.seed)
                pixel_list = []
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_len_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-7)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-7)
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                
                # insert msg bit
                counter = 0
                while(counter < len(msg_bit)):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[:7] + msg_bit[counter]
                    self.frame[height_byte][width_byte][rgb_byte] = int(bits,2)
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-7)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-7)
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
        # next here
        cv2.imwrite('temp/%d.jpg' % frame_byte, self.frame)
        self.frame = ''
    
    def extract_message(self):
        msg_bit = ''

        frame_byte = 0
        width_byte = 0
        height_byte = 0
        rgb_byte = 0
        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
        print(self.frame[height_byte][width_byte])
        
        bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
        self.random_frame_state = int(bits)
        # print(bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8))
        
        rgb_byte += 1

        bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
        self.random_pixel_state = int(bits)
        # print(bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8))
        rgb_byte += 1
       
        if (self.random_frame_state==0):
            if (self.random_pixel_state==0):
                msg_len_bit = ''
                for i in range(32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    # print('binary ',i,': ',bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8))
                    msg_len_bit += bits
                    rgb_byte += 1
                    # change frame if 1 pixel already steg
                    if (rgb_byte > 2):
                        rgb_byte = 0
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-3):
                            frame_byte = 0
                            height_byte += 1
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)

                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1
                
                msg_len = int(msg_len_bit[:8],2)*(2**24) + int(msg_len_bit[8:16],2)*(2**16) + int(msg_len_bit[16:24],2)*(2**8) + int(msg_len_bit[24:],2)
                print('msg_len_bit:',msg_len_bit)
                print('msg_len:',msg_len)
                for i in range(msg_len*8):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_bit += bits
                    rgb_byte += 1
                    # change frame if 1 pixel already steg
                    if (rgb_byte > 2):
                        rgb_byte = 0
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-3):
                            frame_byte = 0
                            height_byte += 1
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                    
                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1

            else:
                msg_len_bit = ''
                random.seed(self.seed)
                pixel_list = []
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_len_bit += bits
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        rgb_byte = 0
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-3):
                            frame_byte = 0 
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                
                msg_len = int(msg_len_bit[:8],2)*(2**24) + int(msg_len_bit[8:16],2)*(2**16) + int(msg_len_bit[16:24],2)*(2**8) + int(msg_len_bit[24:],2)
                # insert message bit
                counter = 0
                while(counter < msg_len*8):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_bit += bits
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte += 1
                        if (frame_byte >= self.num_frames-3):
                            frame_byte = 0 
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)

        else:
            if (self.random_pixel_state==0):
                msg_len_bit = ''
                random.seed(self.seed)
                pixel_list = []
                frame_counter = self.num_frames - 3
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_len_bit += bits
                    
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        frame_counter -= 1
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-4)

                        if (frame_counter==0):
                            height_byte += 1
                            frame_counter = self.num_frames -3

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-4)

                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        
                    if (height_byte >= self.frame_height):
                        height_byte = 0
                        width_byte += 1

                msg_len = int(msg_len_bit[:8],2)*(2**24) + int(msg_len_bit[8:16],2)*(2**16) + int(msg_len_bit[16:24],2)*(2**8) + int(msg_len_bit[24:],2)
                counter = 0
                while(counter < msg_len*8):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_bit += bits
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        frame_counter -= 1
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-4)

                        if (frame_counter==0):
                            height_byte += 1
                            frame_counter = self.num_frames - 3

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-4)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                        
                    if (height_byte >= self.frame_height):
                        height_byte = 0 
                        width_byte += 1
            else:
                msg_len_bit = ''
                random.seed(self.seed)
                pixel_list = []
                # insert msg length
                counter = 0
                while(counter < 32):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_len_bit += bits
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-4)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-4)
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
                
                msg_len = int(msg_len_bit[:8],2)*(2**24) + int(msg_len_bit[8:16],2)*(2**16) + int(msg_len_bit[16:24],2)*(2**8) + int(msg_len_bit[24:],2)
                counter = 0
                while(counter < msg_len*8):
                    bits = bin(self.frame[height_byte][width_byte][rgb_byte])[2:].zfill(8)[7]
                    msg_bit += bits
                    rgb_byte += 1
                    counter += 1

                    # change frame if 1 pixel already steg, random pixel at next frame
                    if (rgb_byte > 2):
                        pixel_list.append([frame_byte,height_byte,width_byte])
                        # cv2.imwrite('temp\%d.jpg' % frame_byte, self.frame)
                        rgb_byte = 0
                        frame_byte = random.randint(0,self.num_frames-4)
                        height_byte = random.randint(0,self.frame_height-1)
                        width_byte = random.randint(0,self.frame_width-1)

                        while([frame_byte,height_byte,width_byte] in pixel_list):
                            frame_byte = random.randint(0,self.num_frames-4)
                            height_byte = random.randint(0,self.frame_height-1)
                            width_byte = random.randint(0,self.frame_width-1)
                        
                        self.frame = cv2.imread('temp/%d.jpg' % frame_byte)
        
        self.message = ''
        while(len(msg_bit) > 0):
            self.message += chr(int(msg_bit[:8],2))
            msg_bit = msg_bit[8:]

    def write_file(self):
        size = (self.frame_width, self.frame_height)
        out = cv2.VideoWriter('temp_video.avi',cv2.VideoWriter_fourcc(*'DIVX'),self.fps,size)
        frame = cv2.imread('temp/0.jpg')
        # frame_rgb = cv2.cvtColor(frame, )
        print(frame)
        for i in range(self.num_frames-6):
            frame = cv2.imread('temp/%d.jpg' % i)
            out.write(frame)

        out.release()

        if os.path.exists('temp'):
            shutil.rmtree('temp')
        
        # m = movie(self.filename)
        # mu = m.extract_music()
        # n = movie('temp_video.avi')
        # final = n+mu
        # final.save(self.save_as)
        # final.clear()

                    

        

if __name__ == '__main__':
    message = 'test123'
    save_as = 'new_sample.avi'
    # vid = video_steg('sample.avi',message=message,save_as=save_as)
    # vid.steganography()
    # vid.write_file()
    # vid = video_steg('temp_video.avi')
    # vid.extract_message()
    # print(vid.message)
    # print(len(vid.message))