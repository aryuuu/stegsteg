import math
import random

class AudioSteg:
    def __init__(self, filename, message='', seed=0, random_state=0, save_as=''):
        f = open(filename,'rb')
        self.format_chunck = f.read(44)
        
        self.data = bytearray(f.read())

        self.seed = seed
        self.message = message
        self.random_state = random_state

        if (save_as==''):
            self.save_as = filename
        else:
            self.save_as = save_as

        f.close()

    def steganograph(self):
        # 1 byte for random state, 3*8 byte for message length
        if(len(self.message)*8 + 3*8 + 1 > len(self.data)):
            return 'message is too long'
        
        else:
            msg_bit = ''.join(format(i, 'b').zfill(8) for i in bytearray(self.message, encoding='utf-8'))
            if (self.random_state==0):
                #insert random state
                bits = bin(self.data[0])[2:].zfill(8)[:7] + '0'
                self.data[0] = int(bits,2)

                #insert message length
                msg_len_bit = bin(len(self.message))[2:].zfill(24)
                msg_length = int(msg_len_bit[:8],2)*(2**16) + int(msg_len_bit[8:16],2)*(2**8) + int(msg_len_bit[16:],2)

                for i in range(24):
                    bits = bin(self.data[i+1])[2:].zfill(8)[:7] + msg_len_bit[i]
                    self.data[i+1] = int(bits,2)

                #insert message
                for i in range(len(msg_bit)):
                    bits = bin(self.data[i+25])[2:].zfill(8)[:7] + msg_bit[i]
                    self.data[i+25] = int(bits,2)   
            else:
                byte_list = []
                
                bits = bin(self.data[0])[2:].zfill(8)[:7] + '1'
                self.data[0] = int(bits,2)
                byte_list.append(0)
                
                random.seed(self.seed)
                
                #insert message length
                msg_len_bit = bin(len(self.message))[2:].zfill(24)
                while(len(msg_len_bit) > 0):
                    rand = random.randint(0,len(self.data)-1)
                    
                    if (rand not in byte_list):
                        bits = bin(self.data[rand])[2:].zfill(8)[:7] + msg_len_bit[0]
                        self.data[rand] = int(bits,2)
                        msg_len_bit = msg_len_bit[1:]
                        byte_list.append(rand)

                #insert message
                while(len(msg_bit) > 0):
                    rand = random.randint(0,len(self.data)-1)
                    
                    if (rand not in byte_list):
                        bits = bin(self.data[rand])[2:].zfill(8)[:7] + msg_bit[0]
                        self.data[rand] = int(bits,2)
                        msg_bit = msg_bit[1:]
                        byte_list.append(rand)
            
    def read_steg(self):
        bits = int(bin(self.data[0])[2:].zfill(8)[7])
        
        if (bits==0):
            self.random_state = 0
        else:
            self.random_state = 1

        if (self.random_state==0):
            #get message length bit
            msg_len_bit = ''
            for i in range(24):
                bit = bin(self.data[i+1])[2:].zfill(8)[7]
                msg_len_bit += bit

            msg_length = int(msg_len_bit[:8],2)*(2**16) + int(msg_len_bit[8:16],2)*(2**8) + int(msg_len_bit[16:],2)
            
            message_bit = ''
            
            for i in range(msg_length*8):
                bit = bin(self.data[i+25])[2:].zfill(8)[7]
                message_bit += bit
        else:
            byte_list = [0]
            random.seed(self.seed)
            msg_len_bit = ''
            counter = 24

            #get message length bit
            while(counter > 0):
                rand = random.randint(0,len(self.data)-1)
                if (rand not in byte_list):
                    bit = bin(self.data[rand])[2:].zfill(8)[7]
                    msg_len_bit += bit
                    counter -= 1
                    byte_list.append(rand)
            
            msg_length = int(msg_len_bit[:8],2)*(2**16) + int(msg_len_bit[8:16],2)*(2**8) + int(msg_len_bit[16:],2)

            #get message bit
            message_bit = ''
            counter = 8*msg_length

            while(counter > 0):
                rand = random.randint(0,len(self.data)-1)
                if (rand not in byte_list):
                    bit = bin(self.data[rand])[2:].zfill(8)[7]
                    message_bit += bit
                    counter -= 1
                    byte_list.append(rand)

        #convert message bit to message
        self.message = ''
        while(len(message_bit) > 0):
            self.message += chr(int(message_bit[:8],2))
            message_bit = message_bit[8:]

    def write_files(self):
        data = bytearray(self.format_chunck)
        data += bytearray(self.data)

        data = bytes(data)

        f = open(self.save_as, 'wb')
        f.write(data)
        f.close()


if __name__ == '__main__':
    option = int(input('Insert steganograph(1)/read steganograph(2): '))
    if (option==1):
        filename = input('Filename: ')
        random_state = int(input('random (0/1): '))
        if (random_state):
            seed = int(input('Seed: '))
        else:
            seed = 0
        
        message = input('message: ')
        save_as = input('save file as: ')

        audio = AudioSteg(filename=filename, message=message, seed=seed, random_state=random_state, save_as=save_as)

        audio.steganograph()
        audio.write_files()
    else:
        filename = input('Filename: ')
        random_state = int(input('random (0/1): '))
        if (random_state):
            seed = int(input('Seed: '))
        else:
            seed = 0

        audio = AudioSteg(filename=filename, seed=seed, random_state=random_state)
        audio.read_steg()
        message = audio.message
        print('the message is: ',message)





