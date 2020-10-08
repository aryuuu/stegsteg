import math
import random
import time

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
            return 0
        
        else:
            # msg_bit = ''.join(format(i, 'b').zfill(8) for i in bytearray(self.message, encoding='utf-8'))
            # print(len(self.message))
            # print(len(self.data))
            msg_bit = ''.join(format(i, 'b').zfill(8) for i in self.message)
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
                byte_list = list(range(1,len(self.data)))
                
                bits = bin(self.data[0])[2:].zfill(8)[:7] + '1'
                self.data[0] = int(bits,2)
                
                random.seed(self.seed)
                random.shuffle(byte_list)
                
                #insert message length
                msg_len_bit = bin(len(self.message))[2:].zfill(24)
                while(len(msg_len_bit) > 0):
                    
                    # rand = random.choice([i for i in range(0,len(self.data)) if i not in byte_list])
                    # rand = random.randint(0,len(self.data)-1)
                    # start = time.time()
                    rand = byte_list[0]
                    byte_list = byte_list[1:]
                    # end = time.time()
                    # print(rand,'->',len(byte_list),'=>',end-start)
                    # if (rand not in byte_list):
                    bits = bin(self.data[rand])[2:].zfill(8)[:7] + msg_len_bit[0]
                    self.data[rand] = int(bits,2)
                    msg_len_bit = msg_len_bit[1:]
                    byte_list.append(rand)

                #insert message
                while(len(msg_bit) > 0):
                    # rand = random.choice([i for i in range(0,len(self.data)) if i not in byte_list])
                    rand = byte_list[0]
                    byte_list = byte_list[1:]
                    # if (rand not in byte_list):
                    bits = bin(self.data[rand])[2:].zfill(8)[:7] + msg_bit[0]
                    self.data[rand] = int(bits,2)
                    msg_bit = msg_bit[1:]
                    byte_list.append(rand)
            return 1
            
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
            print(msg_length)
            print(len(self.data))
            message_bit = ''
            
            for i in range(msg_length*8):
                bit = bin(self.data[i+25])[2:].zfill(8)[7]
                message_bit += bit
        else:
            byte_list = list(range(1,len(self.data)))
            random.seed(self.seed)
            random.shuffle(byte_list)
            msg_len_bit = ''
            counter = 24

            #get message length bit
            while(counter > 0):
                rand = byte_list[0]
                byte_list = byte_list[1:]
                # if (rand not in byte_list):
                bit = bin(self.data[rand])[2:].zfill(8)[7]
                msg_len_bit += bit
                counter -= 1
                byte_list.append(rand)
            
            msg_length = int(msg_len_bit[:8],2)*(2**16) + int(msg_len_bit[8:16],2)*(2**8) + int(msg_len_bit[16:],2)

            #get message bit
            message_bit = ''
            counter = 8*msg_length

            while(counter > 0):
                rand = byte_list[0]
                byte_list = byte_list[1:]
                # if (rand not in byte_list):
                bit = bin(self.data[rand])[2:].zfill(8)[7]
                message_bit += bit
                counter -= 1
                byte_list.append(rand)

        #convert message bit to message (in bytes)
        
        self.message = int(message_bit,2).to_bytes(msg_length, byteorder='big')
        

    def write_files(self):
        data = bytearray(self.format_chunck)
        data += bytearray(self.data)

        data = bytes(data)

        f = open(self.save_as, 'wb')
        f.write(data)
        f.close()


if __name__ == '__main__':
    option = int(input('Insert message(1) / Extract message(2): '))
    if (option==1):
        filename = input('Filename: ')
        message_type = int(input('message type - input text(0) / txt file(1) / file(2): '))
        if (message_type==0):
            message = input('message: ')
            message = str.encode(message)
        elif (message_type==1):
            txt_filename = input('txt filename: ')
            message_file = open(txt_filename,'r')
            message = message_file.read()
            message = str.encode(message)
            message_file.close()

        elif (message_type==2):
            embed_filename = input('filename: ')
            embed_file = open(embed_filename,'rb')
            message = bytearray(str.encode(embed_filename.split('.')[-1] + '<>'))
            message.extend(embed_file.read())
            message = bytes(message)
            embed_file.close()

        random_state = int(input('random - no (0) / yes (1): '))
        if (random_state):
            key = input('Key :')
            key = key.upper()
            seed = 0
            for k in key:
                seed += ord(k)
            # seed = int(input('Seed: '))
        else:
            seed = 0
        
        save_as = input('save file as: ')

        audio = AudioSteg(filename=filename, message=message, seed=seed, random_state=random_state, save_as=save_as)
        start = time.time()
        if (audio.steganograph()):
            end = time.time()
            audio.write_files()
            print('Message successfully inserted in %f seconds' % (end-start))
        else:
            print('message size is too big')
    else:
        filename = input('Filename: ')
        random_state = int(input('random - no (0) / yes (1): '))
        if (random_state):
            key = input('Key: ')
            key = key.upper()
            seed = 0
            for k in key:
                seed += ord(k)
            # seed = int(input('Seed: '))
        else:
            seed = 0

        audio = AudioSteg(filename=filename, seed=seed, random_state=random_state)
        start = time.time()
        audio.read_steg()
        end = time.time()
        message = audio.message
        if str.encode('<>') in message:
            ext_loc = message.find(str.encode('<>'))
            ext = message[:ext_loc].decode()
            message_byte = message[ext_loc+2:]
            f = open('message.'+ext, 'wb')
            f.write(message_byte)
            f.close()
            print('Message file has been extracted in %f seconds' % (end-start))

        else:
            message = message.decode()
            print('Message has been extracted in %f seconds' % (end-start))
            write_option = int(input('message is in text, want to write it to txt file? yes(1)/no(0): '))
            if (write_option):
                f = open('message.txt','w')
                f.write(message)
                f.close()       
            else: 
                print('the message is: ',message)





