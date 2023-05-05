#statsGUI by William Reid started 12/11/2021
#main
from threading import Thread
import logging
import time
import datetime
import asyncio
# from pprint import pprint
from api_call import clean_agent_data, get_queue_data, clean_queue_data, get_agent_data

from wallboard_functions import *

logging.basicConfig(filename=f'{datetime.datetime.now().strftime("%a, %d %B %Y")}.txt',
                    format='%(asctime)s %(message)s',
                    level=logging.CRITICAL
                    )


## Multithreading Functions and Class ##

class QueueThread(Thread):
    '''
    Defines queue thread class for multithreaded responses
    '''
    def __init__(self):
        Thread.__init__(self)
        self.queue_value = None
    def run(self):
        self.queue_value =  clean_queue_data(asyncio.run(get_queue_data(queue_query_list)))


class AgentThread(Thread):
    '''
    Defines agent thread class for multithreaded responses
    '''
    def __init__(self):
        Thread.__init__(self)
        self.agent_value = None
    def run(self):
        self.agent_value =  clean_agent_data(asyncio.run(get_agent_data(email_list)))
        

def create_agent_thread() -> Thread:
    '''
    Sets thread as agent thread class to re-exec thread
    '''
    thread = AgentThread()
    return thread

def create_queue_thread() -> Thread:
    '''
    Sets thread as queue thread class to re-exec thread
    '''
    thread = QueueThread()
    return thread


### config ###

DEFAULT_ROW_X = 180
DEFAULT_ROW_Y = 24

DEFAULT_BLOCK_WIDTH = 180
DEFAULT_BLOCK_HEIGHT = 24

QUEUE_DEFAULT_ROW_X = 160
QUEUE_DEFAULT_BLOCK_WIDTH = 160

QUEUE_ENABLED = True
AGENTS_ENABLED = True

### init variables ###

clock = pygame.time.Clock()
t = time.localtime()

REFRESH_TIME = 2 # seconds
TICK_RATE = 2.5 #ticks per second
TIMER = 0

sla_thermometer.draw()
SLA_THERMOMETER_STRING = "0"

### main loop ###

IS_RUNNING = True

email_list_initial = [agent.email for agent in agent_list if "@dxc" in agent.email]


CHUNK = 1
#List of list - emails split for iteration
email_list = [email_list_initial[i:i+CHUNK] for i in range(0, len(email_list_initial), CHUNK)]
queue_query_list = [
            ["CBA Desktop Hardware New"],
            ["CBA Desktop Hardware Existing"],
            ["CBA Desktop Business Apps New"],
            ["CBA Desktop Business Apps Existing"],
            ["CBA Desktop CommSee New"],
            ["CBA Desktop CommSee Existing"],
            ["CBA Desktop Pwd"]
        ]

while IS_RUNNING:
    logging.info("test")
    current_time = datetime.datetime.now()

    clock.tick(TICK_RATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            IS_RUNNING = False

    window_surface.blit(background, (0, 0))

     # loading bar down the bottom
    pygame.draw.rect(background,(1+(5*TIMER),1+(5*TIMER),1+(5*TIMER)),((54,1050),(72*(TIMER+1),8)))

    if TIMER >= (TICK_RATE * REFRESH_TIME):
        TIMER = 0

        start = time.time()
        
        t1 = create_agent_thread()
        t2 = create_queue_thread()

        t1.start()
        t2.start()

        t1.join()
        t2.join()


        print(f"Elapsed response time: {time.time() - start}")

        print("- new call ----------------------------------------------------------------")
        #not implemetnsed neeed further api functions
        # NPT_READER keys: "Agent","Nonproductive time","Online time","Outbound Call time
        NPT_READER = None

        if(AGENTS_ENABLED):
            # KEYS: "Agent","Activity","Duration","Agent Name","Handled in","Handled out","AHT"
            agent_reader = t1.agent_value
            ROW_NUMBER = 1
            if agent_reader is not None:
                print(f"Agents: {len(agent_reader)}")
                # this is O(n^2) :(
                for agent in agent_list:
                    NPT_FOUND = False
                    AGENT_NPT = None
                    if False:
                        for npt in NPT_READER:
                            if npt["Agent"] == (agent.email):
                                true_npt_seconds = (int(npt["Nonproductive time"]) - int(npt["Outbound Call time"]))
                                AGENT_NPT = str(datetime.timedelta(seconds = true_npt_seconds))
                                NPT_FOUND = True
                                break #stop looking for npt for agents

                    FOUND_ROW = False
                    for row in agent_reader: #list of dicts
                        if row['Agent'] == agent.email: #if email adress in row matches agent email

                            FOUND_ROW = True
                            agent.is_online = True
                            #create or update agent's GUI row
                            if AGENT_NPT:
                                row["True NPT"] = AGENT_NPT
                            else:
                                row["True NPT"] = "-"


                            if row["Activity"] == "":
                                print(f"Null activity found, {agent.email}")
                                row["Activity"] = 'ACW'
                                agent.agent_row(ROW_NUMBER,
                                                DEFAULT_ROW_X,
                                                DEFAULT_ROW_Y,
                                                DEFAULT_BLOCK_WIDTH,
                                                DEFAULT_BLOCK_HEIGHT,
                                                row)
                                break
                            elif row["Activity"] != " ":
                                agent.agent_row(ROW_NUMBER,
                                                DEFAULT_ROW_X,
                                                DEFAULT_ROW_Y,
                                                DEFAULT_BLOCK_WIDTH,
                                                DEFAULT_BLOCK_HEIGHT,
                                                row)

                                break
                            else:
                                print(row['Agent'] + " failed!")

                    if FOUND_ROW is False:
                        if agent.is_online:
                            agent.count_failures()
                        else:
                            agent.agent_row(ROW_NUMBER,
                                            DEFAULT_ROW_X,
                                            DEFAULT_ROW_Y,
                                            DEFAULT_BLOCK_WIDTH,
                                            DEFAULT_BLOCK_HEIGHT,
                                            {"Agent" : agent.email,
                                            "Activity" : "Offline",
                                            "Duration" : "EoS",
                                            "Agent Name" : agent.l_name + ", " + agent.f_name,
                                            "Handled in" : "-",
                                            "Handled out" : "-",
                                            "AHT" : "00:00:00",
                                            "True NPT" : "-"}
                                            )
                    ROW_NUMBER += 1

        if(QUEUE_ENABLED):
            #KEYS: "Name","Online","NPT","In queue","Oldest","Queued","Handled","Abandoned","AHT","SL 60 secs"
            queue_reader = t2.queue_value
            
            try:
                if queue_reader != None:
                    for queue in queue_list:
                        if queue.name == "Queue":
                            heading_row = {
                            'Name': "",
                            'Online': "",
                            'In queue': "",
                            'Oldest': "",
                            'Queued': "",
                            'Handled': "",
                            'Abandoned': "",
                            'AHT': "",
                            'SL 60 secs': "",
                            }
                            queue.queue_row(queue_list.index(queue)+1,
                                            QUEUE_DEFAULT_ROW_X,
                                            DEFAULT_ROW_Y,
                                            QUEUE_DEFAULT_BLOCK_WIDTH,
                                            DEFAULT_BLOCK_HEIGHT,
                                            heading_row)


                        for queue_row in queue_reader:
                            if queue_row["Name"] == queue.name:
                                queue.queue_row(queue_list.index(queue)+1,
                                                QUEUE_DEFAULT_ROW_X,
                                                DEFAULT_ROW_Y,
                                                QUEUE_DEFAULT_BLOCK_WIDTH,
                                                DEFAULT_BLOCK_HEIGHT,
                                                queue_row)
                            if queue_row["Name"] == "Summary":
                                SLA_THERMOMETER_STRING = queue_row["SL 60 secs"]
            except:
                logging.critical('The program crashed - unable to continue')
                logging.critical(f'{datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S")}')
                logging.critical(f'Output of queue_reader was: {queue_reader}')
                logging.critical(f'Queue reader type is {type(queue_reader)}')

        if agent_reader is not None:
            stats_available.reset_count()
            stats_on_contact.reset_count()
            stats_ticketing.reset_count()
            stats_on_break.reset_count()
            stats_offline.reset_count()
            stats_other.reset_count()

            for status in agent_reader:
                match status['Activity']:
                    case "Available":
                        stats_available.amount += 1
                    case "On Contact" | "Incoming" | "Outbound Call":
                        stats_on_contact.amount += 1
                    case "Ticketing":
                        stats_ticketing.amount += 1
                    case "Short Break" | "Lunch Break" | "Comfort Break":
                        stats_on_break.amount += 1
                    case "Offline":
                        stats_offline.amount += 1
                    case _:
                        stats_other.amount += 1

        for stats in stats_list:
            stats.stats_row(stats_list.index(stats)+1,
                            QUEUE_DEFAULT_ROW_X,
                            DEFAULT_ROW_Y,
                            QUEUE_DEFAULT_BLOCK_WIDTH,
                            DEFAULT_BLOCK_HEIGHT)


    TIMER += 5

    sla_thermometer.update(SLA_THERMOMETER_STRING)
    sla_thermometer.draw()

    pygame.display.update()
