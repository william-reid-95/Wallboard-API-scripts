#statsGUI by William Reid started 12/11/2021

#initilization and function definitions

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame #graphics
import csv

win_x, win_y = 1920, 1080

pygame.init()

pygame.display.set_caption('Wallboard')

window_surface = pygame.display.set_mode((win_x, win_y))

background = pygame.Surface((win_x, win_y))

background.fill(pygame.Color(150,150,150))

font = pygame.font.SysFont(None, 24)

icon = pygame.image.load(r'assets\icon.ico') 
pygame.display.set_icon(icon)

#logo = pygame.image.load(r"assets\big.png")

bg_colour = (0,0,0) #background colour

### BODY

pygame.draw.rect(background,(0,0,0),((10,10),(1920-20,1080-20)))
pygame.draw.rect(background,(224,224,224),((1445,26),(405,75)))

#background.blit(logo,(1492,25))

###################  GUI OBJECTS  #####################

def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class Thermometer():
    def __init__(self,x_pos,y_pos,x_mag,y_mag):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_mag = x_mag
        self.y_mag = y_mag
        self.colour = (0,255,0) #tuple RGB

        self.y_mag2 = y_mag

    def update(self,SLA_string):
        """draw a new thermometer on the screen"""
        SLA_int = int(float(SLA_string))
        #print(SLA_int)
        self.y_mag2 = self.y_mag - (4 * SLA_int)
        #print(self.y_mag2)
        if SLA_int > 50:
            self.colour = (255-SLA_int,255,0)
        elif SLA_int < 50:
            self.colour = (255,205+SLA_int,0)
        else:
            self.colour = (255,255,0)
        #pass this functiont he sla strign and it will change hte size and colour of the rectangle

    def draw(self):
        #draw rectangle
        pygame.draw.rect(background,self.colour,((self.x_pos,self.y_pos),(self.x_mag,self.y_mag)))
        pygame.draw.rect(background,bg_colour,((self.x_pos,self.y_pos),(self.x_mag,self.y_mag2)))
        self.text = font.render("SLA",True,(0,0,0))
        background.blit(self.text,(1752,980))

pygame.draw.rect(background,(224,224,224),((1740,595),(60,410)))
sla_thermometer = Thermometer(1745,600,50,400)


class Block: 
    def __init__(self,x_pos,y_pos,x_mag,y_mag,string,colour):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_mag = x_mag
        self.y_mag = y_mag
        self.string = string
        self.colour = colour # tuples (r,g,b,alpha (alpha optional))

    def draw(self, underline = False):
        #draw rectangle
        pygame.draw.rect(background,self.colour,((self.x_pos,self.y_pos),(self.x_mag,self.y_mag)))
        if underline:
            pygame.draw.rect(background,(0,0,0),((self.x_pos+2,self.y_pos+(self.y_mag-4)),(self.x_mag-4,2)))

        #draw text
        self.text = font.render(str(self.string),True,(0,0,0)) #(0,0,0) is the colour of the font - black
        background.blit(self.text,(self.x_pos,self.y_pos+4))

    def update(self,new_string,new_colour,new_underline = False):
        self.string = new_string
        self.colour = new_colour
        self.draw(underline = new_underline)


row_list = []

class GUI_Row:
    def __init__(self,row_number, row_x, row_y, block_height, block_width, csv_row, is_sme, is_commsee, is_heading, is_blank):
        self.row_number = row_number # which row
        self.row_x = row_x # pos x
        self.row_y = row_y
        self.block_height = block_height
        self.block_width = block_width

        self.csv_row = csv_row
        
        self.is_sme = is_sme
        self.is_commsee = is_commsee
        self.is_heading = is_heading
        self.is_blank = is_blank
        self.show_heading_titles = True

        self.gap = 2 #capitalise as is constant
        self.offset_x = 30 #capitalise as is constant
        self.offset_y = 0 #capitalise as is constant

        self.agent_block = None
        self.activity_block = None
        self.duration_block = None
        self.in_block = None
        self.out_block = None
        self.average_block = None
        self.npt_block = None
        
        row_list.append(self)

        

        if row_number >= 40: #second row of agents
            self.offset_x = (self.offset_x + win_x/2)-300
            self.offset_y = 988+26

    def get_colour(self,value,threshold) -> tuple:
        if self.is_heading == False:
            colour = None
            if value >= threshold:
                colour = (255,0,0)
            else:
                if(self.row_number % 2) == 0:
                    colour = (224,224,224)
                else:
                    colour = (200,200,200)
            return colour
        else:
            return (150,150,150)

    def update(self):
         #blank

        if self.is_heading == False and self.is_blank == False:# if not headings, change colour of row based on activity
            if self.csv_row["Activity"] == "On Contact":
                self.activity_colour = (51,255,255)#cyan
            elif self.csv_row["Activity"] == "On Hold":
                self.activity_colour = (51,255,255)#cyan
            elif self.csv_row["Activity"] == "Available":
                self.activity_colour = (51,255,51)#green
            elif self.csv_row["Activity"] == "Incoming":
                self.activity_colour = (51,255,51)#green
            elif self.csv_row["Activity"] == "Outbound Call":
                self.activity_colour = (153,51,255)#purple
            elif self.csv_row["Activity"] == "Training/Coaching":
                self.activity_colour = (255,255,51)#yellow
                self.csv_row["Activity"] = "Training"
            elif self.csv_row["Activity"] == "Meetings/Huddles":
                self.activity_colour = (255,255,51)#yellow
                self.csv_row["Activity"] = "Meetings"
            elif self.csv_row["Activity"] == "Projects (Internal)":
                self.activity_colour = (255,255,51)#yellow
                self.csv_row["Activity"] = "Projects"
            elif self.csv_row["Activity"] == "Missed":
                self.activity_colour = (255,153,51)#orange
            elif self.csv_row["Activity"] == "Ticketing/Research":
                self.activity_colour = (255,153,51)#orange
                self.csv_row["Activity"] = "Ticketing"
            elif self.csv_row["Activity"] == "After contact work":
                self.activity_colour = (255,153,51)#orange
                self.csv_row["Activity"] = "Ticketing"
            elif self.csv_row["Activity"] == "Short Break":
                self.activity_colour = (224,224,224)#light grey
            elif self.csv_row["Activity"] == "Lunch Break":
                self.activity_colour = (224,224,224)#light grey
            elif self.csv_row["Activity"] == "Comfort Break":
                self.activity_colour = (224,224,224)#dark grey
            elif self.csv_row["Activity"] == "Offline Tasks":
                self.activity_colour = (255, 0, 255)#pink
            elif self.csv_row["Activity"] == "System Down":
                self.activity_colour = (255, 0, 255)#pink
            elif self.csv_row["Activity"] == "Offline":
                self.activity_colour = (255,51,51)#red
            else:
                self.activity_colour = (255,51,51)#red

        elif self.is_heading == True and self.is_blank == False:
            self.activity_colour = (150,150,150)
            if self.show_heading_titles == True:
                self.csv_row["Handled in"] = "In"
                self.csv_row["Handled out"] = "Out"
                self.csv_row["AHT"] = "AHT"
                self.csv_row["True NPT"] = "NPT"
                self.csv_row["Duration"] = "Duration"
                self.csv_row["Activity"] = "Activity"

            else:
                self.csv_row["Handled in"] = ""
                self.csv_row["Handled out"] = ""
                self.csv_row["AHT"] = ""
                self.csv_row["True NPT"] = ""
                self.csv_row["Duration"] = ""

        elif self.is_heading == False and self.is_blank == True:
            self.activity_colour = (0,0,0)

        ###Flag agents over a certain duration

        self.flag = False
        try: #mark agents who are over duration
            if self.is_heading == False and self.is_sme == False:
                if self.csv_row["Activity"] == "On Contact" and get_sec(self.csv_row["Duration"]) >= 1200:
                    self.flag = True
                elif self.csv_row["Activity"] == "Ticketing" and get_sec(self.csv_row["Duration"]) >= 600:
                    self.flag = True
                elif self.csv_row["Activity"] == "Lunch Break" and get_sec(self.csv_row["Duration"]) >= 3600:
                    self.flag = True
                elif self.csv_row["Activity"] == "Short Break" and get_sec(self.csv_row["Duration"]) >= 600:
                    self.flag = True
        except:
            #do nothing if error (instead of crashing)
            pass

        self.npt_flag = False
        try: #mark agents who are over duration with a ! 
            if self.is_heading == False and get_sec(self.csv_row["True NPT"]) >= 7200:
                self.npt_flag = True
            else:
                self.npt_flag = False
                
        except:
            #do nothing if error (instead of crashing)
            pass

        if self.is_sme:
            if self.csv_row["Activity"] == "Offline Tasks":
                self.csv_row["Activity"] = "Online"
                self.activity_colour = (51,255,51)


        #THESE NEED TO BE FUNCTIONS AS ITS BASICALLY THE SAME THING HAPPENING 6 TIMES, but it does work :)

        if 'Agent Name' in self.csv_row:
            if self.agent_block == None:# this fixes infinite duplication bug but is a huge pain in this ass
                self.agent_block = Block(self.row_x*0+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height, self.block_width,self.csv_row['Agent Name'],self.activity_colour)
                self.agent_block.draw()
            else:
                self.agent_block.update(" " + self.csv_row['Agent Name'],self.activity_colour)


        if 'Activity' in self.csv_row:
            if self.is_sme == False:
                if self.activity_block == None:
                    self.activity_block = Block(self.row_x*1+self.offset_x+2,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-48, self.block_width,self.csv_row['Activity'],self.activity_colour)
                    self.activity_block.draw()
                else:
                    self.activity_block.update(" " + self.csv_row['Activity'],self.activity_colour,self.flag)
            else:
                if self.activity_block == None:
                    self.activity_block = Block(self.row_x*1+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height+20, self.block_width,self.csv_row['Activity'],self.activity_colour)
                    self.activity_block.draw()
                else:
                    self.activity_block.update(" " + self.csv_row['Activity'],self.activity_colour,self.flag)

        ## Non SME Blocks

        if 'Duration'in self.csv_row and self.is_sme == False:
            if self.duration_block == None:
                self.duration_block = Block(self.row_x*2+self.offset_x-48,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-96, self.block_width,self.csv_row['Duration'],self.activity_colour)
                self.duration_block.draw(underline=self.flag)
            else:
                self.duration_block.update(" " + self.csv_row['Duration'],self.activity_colour,self.flag)


        if 'Handled in' in self.csv_row and self.is_sme == False:
            if self.in_block == None:
                self.in_block = Block((self.row_x*3)-142+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-140, self.block_width,self.csv_row['Handled in'],self.activity_colour)
                self.in_block.draw()
            else:
                self.in_block.update(" " + self.csv_row['Handled in'],self.activity_colour)

        if 'Handled out' in self.csv_row and self.is_sme == False:
            if self.out_block == None:
                self.out_block = Block((self.row_x*4)-280+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-140, self.block_width,self.csv_row['Handled out'],self.activity_colour)
                self.out_block.draw()
            else:
                self.out_block.update(" " + self.csv_row['Handled out'],self.activity_colour)

        if 'AHT' in self.csv_row and self.is_sme == False:
            if self.average_block == None:
                self.average_block = Block((self.row_x*5)-418+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-100, self.block_width,self.csv_row['AHT'],self.activity_colour)
                self.average_block.draw()
            else:
                self.average_block.update(" " + self.csv_row['AHT'],self.activity_colour)
        
        if 'True NPT' in self.csv_row and self.is_sme == False:
            if self.npt_block == None:
                self.npt_block = Block((self.row_x*6)-516+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-100, self.block_width,self.csv_row['True NPT'],self.activity_colour)
                self.npt_block.draw()
            else:
                #UPDATE npt block not working for some reason
                
                self.npt_block.x_pos = (self.row_x*6)-516+self.offset_x
                self.npt_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.npt_block.x_mag = self.block_height-100
                self.npt_block.y_mag = self.block_width
                self.npt_block.string = " " + self.csv_row['True NPT']
                self.npt_block.colour = self.activity_colour
                self.npt_block.draw(self.npt_flag)

class GUI_Row_Queue:
    def __init__(self,row_number, row_x, row_y, block_height, block_width, csv_row, description):
        self.row_number = row_number # which row
        self.row_x = row_x # pos x
        self.row_y = row_y
        self.block_height = block_height
        self.block_width = block_width

        self.csv_row = csv_row
        self.description = description

        self.gap = 2
        self.offset_x = 50
        self.offset_y = -120

        self.name_block = None
        self.in_queue_block = None
        self.queued_block = None

        self.SLA_block = None
        self.longest_wait_block = None


        row_list.append(self)


        self.offset_x = (self.offset_x + win_x/2+320)+50

        #TODO: logic to change colour based on queue volume

        if self.description == ' Queues':
            self.activity_colour = (150,150,150)


    def update(self):

        if self.description != ' Queues':
            if int(self.csv_row["In queue"]) >= 1:
                self.activity_colour = (255,0,0)
            else:
                if(self.row_number % 2) == 0:
                    self.activity_colour = (224,224,224)
                else:
                    self.activity_colour = (200,200,200)

        if self.description == ' Queues':
            self.csv_row["In queue"] = "In Q"
            self.csv_row["Handled"] = "Total"
            self.csv_row["SL 60 secs"] = "SLA"
            self.csv_row["Oldest"] = "Wait"


        #THESE NEED TO BE FUNCTIONS AS ITS BASICALLY THE SAME THING HAPPENING 6 TIMES, but it does work :)
        if "Name" in self.csv_row:
            if self.name_block == None: 
                self.name_block = Block(self.row_x*0+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height, self.block_width,self.description,self.activity_colour)
                self.name_block.draw()
            else:
                #UPDATE BLOCK
                self.name_block.x_pos = self.row_x*0+self.offset_x
                self.name_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.name_block.x_mag = self.block_height
                self.name_block.y_mag = self.block_width
                self.name_block.string = self.description
                self.name_block.colour = self.activity_colour
                self.name_block.draw()

        if "In queue" in self.csv_row:
            if self.in_queue_block == None:
                self.in_queue_block = Block(self.row_x*1+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-100, self.block_width,self.csv_row["In queue"],self.activity_colour)
                self.in_queue_block.draw()
            else:
                #UPDATE BLOCK
                self.in_queue_block.x_pos = self.row_x*1+self.offset_x
                self.in_queue_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.in_queue_block.x_mag = self.block_height-100
                self.in_queue_block.y_mag = self.block_width
                self.in_queue_block.string = self.csv_row["In queue"]
                self.in_queue_block.colour = self.activity_colour
                self.in_queue_block.draw()

        if "Handled" in self.csv_row:
            if self.queued_block == None:
                self.queued_block = Block(self.row_x*2+self.offset_x-100,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-80, self.block_width,self.csv_row["Handled"],self.activity_colour)
                self.queued_block.draw()
            else:
                #UPDATE BLOCK
                self.queued_block.x_pos = self.row_x*2+self.offset_x-100
                self.queued_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.queued_block.x_mag = self.block_height-80
                self.queued_block.y_mag = self.block_width
                self.queued_block.string = self.csv_row["Handled"]
                self.queued_block.colour = self.activity_colour
                self.queued_block.draw()

        if "SL 60 secs" in self.csv_row:
            if self.SLA_block == None:
                self.SLA_block = Block(self.row_x*3+self.offset_x-200,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-80, self.block_width,self.csv_row["SL 60 secs"],self.activity_colour)
                self.SLA_block.draw()
            else:
                #UPDATE BLOCK
                self.SLA_block.x_pos = self.row_x*3+self.offset_x-200
                self.SLA_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.SLA_block.x_mag = self.block_height-80
                self.SLA_block.y_mag = self.block_width
                self.SLA_block.string = self.csv_row["SL 60 secs"]
                self.SLA_block.colour = self.activity_colour
                self.SLA_block.draw()
        
        if "Oldest" in self.csv_row:
            if self.longest_wait_block == None:
                self.longest_wait_block = Block(self.row_x*4+self.offset_x-280,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-40, self.block_width,self.csv_row["Oldest"],self.activity_colour)
                self.longest_wait_block.draw()
            else:
                #UPDATE BLOCK
                self.longest_wait_block.x_pos = self.row_x*4+self.offset_x-280
                self.longest_wait_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
                self.longest_wait_block.x_mag = self.block_height-80
                self.longest_wait_block.y_mag = self.block_width
                self.longest_wait_block.string = self.csv_row["Oldest"]
                self.longest_wait_block.colour = self.activity_colour
                self.longest_wait_block.draw()

class GUI_Row_Stats:
    def __init__(self,row_number, row_x, row_y, block_height, block_width, stats_amount, description):
        self.row_number = row_number # which row
        self.row_x = row_x # pos x
        self.row_y = row_y
        self.block_height = block_height
        self.block_width = block_width

        self.stats_amount = stats_amount
        self.description = description

        self.gap = 2
        self.offset_x = 50
        self.offset_y = -400

        self.status_name_block = None
        self.amount_block = None

        row_list.append(self)

        self.offset_x = (self.offset_x + win_x/2+320)+50

        if self.description == ' Summary':
            self.activity_colour = (150,150,150)
            self.stats_amount = ''
        else:
            if(row_number % 2) == 0:
                self.activity_colour = (224,224,224)
            else:
                self.activity_colour = (200,200,200)


    def update(self):
        #THESE NEED TO BE FUNCTIONS AS ITS BASICALLY THE SAME THING HAPPENING 6 TIMES, but it does work :)
        if self.description == ' Summary':
            self.stats_amount = ''

        if self.status_name_block == None:# this fixes infinite duplication bug but is a huge pain in this ass
            self.status_name_block = Block(self.row_x*0+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height, self.block_width,self.description,self.activity_colour)
            self.status_name_block.draw()
        else:
            #UPDATE BLOCK
            self.status_name_block.x_pos = self.row_x*0+self.offset_x
            self.status_name_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
            self.status_name_block.x_mag = self.block_height
            self.status_name_block.y_mag = self.block_width
            self.status_name_block.string = self.description
            self.status_name_block.colour = self.activity_colour
            self.status_name_block.draw()


        if self.amount_block == None:
            self.amount_block = Block(self.row_x*1+self.offset_x,(self.row_y+self.gap)*self.row_number-self.offset_y, self.block_height-100, self.block_width,str(self.stats_amount),self.activity_colour)
            self.amount_block.draw()
        else:
            #UPDATE BLOCK
            self.amount_block.x_pos = self.row_x*1+self.offset_x
            self.amount_block.y_pos = (self.row_y+self.gap)*self.row_number-self.offset_y
            self.amount_block.x_mag = self.block_height-100
            self.amount_block.y_mag = self.block_width
            self.amount_block.string = str(self.stats_amount)
            self.amount_block.colour = self.activity_colour
            self.amount_block.draw()

#############  PRE GUI  ###########

agent_list = []
queue_list = []
stats_list = []

class Agent:
    def __init__(self,email,f_name,l_name,is_sme,is_heading,is_commsee,is_blank):
        self.email = email
        self.f_name = f_name
        self.l_name = l_name

        self.is_sme = is_sme
        self.is_commsee = is_commsee

        self.is_heading = is_heading
        self.is_blank = is_blank


        self.gui_row_instance = None

        self.failed_refresh_count = 0
        self.is_online = True

        agent_list.append(self)

    def agent_row(self, row_number, default_row_x, default_row_y, default_block_width, default_block_height, row):
        if self.gui_row_instance == None:#create row
            self.gui_row_instance = GUI_Row(row_number, default_row_x, default_row_y, default_block_width, default_block_height, row, self.is_sme, self.is_heading,self.is_commsee,self.is_blank)
        else:#update existing row
            self.gui_row_instance.csv_row = row
            self.gui_row_instance.update()

    def count_failures(self):
        self.failed_refresh_count += 1
        if self.failed_refresh_count >= 5:
            self.is_online = False

    

def create_agents():
    with open('agents.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile) 
        for row in reader:
            #determine row type
            if row['IS_SME'] == "TRUE":
                is_sme = True
            else:
                is_sme = False

            if row['IS_COMMSEE'] == "TRUE":
                is_commsee = True
            else:
                is_commsee = False

            if row['IS_HEADING'] == "TRUE":
                is_heading = True
            else:
                is_heading = False

            if row['IS_BLANK'] == "TRUE":
                is_blank = True
            else:
                is_blank = False

            an_agent = Agent(row['EMAIL'], row['F_NAME'], row['L_NAME'], is_sme, is_commsee, is_heading, is_blank)


create_agents()

class Queue:
    def __init__(self, name, description):
        self.name = name
        self.description = description

        self.amount = 0

        self.gui_queue_instance = None

        queue_list.append(self)

    def queue_row(self, row_number, default_row_x, default_row_y, default_block_width, default_block_height, row):
        if self.gui_queue_instance == None:#create row
            self.gui_queue_instance = GUI_Row_Queue(row_number, default_row_x, default_row_y, default_block_width, default_block_height, row, self.description)
        else:#update existing row
            self.gui_queue_instance.csv_row = row
            self.gui_queue_instance.update()

def create_queues():
    # queue headings
    queue_heading = Queue('Queue',' Queues')

    # queues
    queue_summary = Queue('Summary',' Summary')

    queue_Pwd = Queue('CBA Desktop Pwd',' Password')

    queue_hardware_new = Queue('CBA Desktop Hardware New',' Desktop New')
    queue_hardware = Queue('CBA Desktop Hardware Existing',' Desktop Exist.')
    #queue_hidden = Queue('CBA Desktop Hidden',' Desktop Hidden')

    queue_commSee_new = Queue('CBA Desktop CommSee New',' CommSee New')
    queue_commSee = Queue('CBA Desktop CommSee Existing',' CommSee Exist.')

    queue_apps_new = Queue('CBA Desktop Business Apps New',' Bank Apps New')
    queue_apps = Queue('CBA Desktop Business Apps Existing',' Bank Apps Exist.')

create_queues()

###########  STATS  ############

class Stats:
    def __init__(self,description):
        self.description = description

        self.amount = 0

        self.gui_stats_instance = None

        stats_list.append(self)

    def stats_row(self, row_number, default_row_x, default_row_y, default_block_width, default_block_height):
        if self.gui_stats_instance == None:#create row
            self.gui_stats_instance = GUI_Row_Stats(row_number, default_row_x, default_row_y, default_block_width, default_block_height, self.amount, self.description)
        else:#update existing row
            self.gui_stats_instance.stats_amount = self.amount
            self.gui_stats_instance.update()

    def reset_count(self):
        self.amount = 0

stats_available = Stats(' Summary')
stats_available = Stats(' Available')
stats_on_contact = Stats(' On Contact')
stats_ticketing = Stats(' Ticketing')
stats_on_break = Stats(' On Break')
stats_offline = Stats(' Offline')
stats_other = Stats(' Other Activities')
