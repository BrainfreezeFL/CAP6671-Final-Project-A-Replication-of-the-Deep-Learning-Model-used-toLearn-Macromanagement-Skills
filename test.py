import mysql.connector
import re
import numpy as np
#import numpy as np


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Eastshore416!"
)

def return_player_replay_ids(replay_id):
    array = []
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select PlayerReplayID from playerreplay where ReplayID = " + str(replay_id) + " and RaceID = 2 ")
    for i in mycursor:
        array.append(i)
    if array != [] :
        our_player_replay_id = re.findall(digit_pattern, str(array[0]))

    mycursor.execute("select PlayerReplayID from playerreplay where ReplayID = " + str(replay_id) + " and RaceID = 1 ")
    array = []
    for i in mycursor:
        array.append(i)
    if array != [] :
        opp_player_replay_id = re.findall(digit_pattern, str(array[0]))
        return our_player_replay_id[0], opp_player_replay_id[0]
    else :
        return None, None


def return_player_opponent_viewer_ids(replay_id):

    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select ViewerID from visibilitychange where UnitID = (select UnitID from event where ReplayID=" + str(replay_id) + " and EventTypeID=12 and UnitID in (select UnitID from unit where (UnitTypeID between 60 and 61) or (UnitTypeID between 63 and 88) or (UnitTypeID between 154 and 174)) limit 1);")
    array = []
    #print(mycursor)
    #print(mycursor)
    for i in mycursor:
        array.append(i)
    if array != [] :
        #print(array)
        one = re.findall(digit_pattern, str(array[0]))
        if len(array) >= 2 :
            two = re.findall(digit_pattern, str(array[1]))
        else : 
            return str(one[0]), None
        #print(one)
        return str(one[0]), str(two[0])
    else : 
        return None, None

def test_return_player_opponent_viewer_id():
    replay_id = 1
    while replay_id < 100:
        our_replay_id, opp_replay_id = return_player_opponent_viewer_ids(replay_id)
        print("Replay id: " + str(replay_id))
        if our_replay_id != None:
            print("Our replay id: " + our_replay_id)
            print("Opp replay id: " + opp_replay_id)
        replay_id +=1

#test_return_player_opponent_viewer_id()
def return_max_frame_in_a_replay(replay_id):
    none_pattern = re.compile('None')
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select MAX(Frame) from event where ReplayID ="+str(replay_id) + ";")
    array = []
   # print(mycursor)
   
    for i in mycursor:
        #print(re.search(none_pattern, str(i)))
        if re.search(none_pattern, str(i)) == None:
            array.append(i)
    if array != [] :
        #print(str(array[0]))
        one = re.findall(digit_pattern, str(array[0]))
        #two = re.findall(digit_pattern, str(array[1]))
        #print(one)

        return str(one[0])#, str(two[0])
    else : 
        return None


def upgrade_array_without_triggering_event(our_units_array, our_tech_array, our_upgrades_array, replay_id, frame, our_visibility_id, opp_visibility_id): 
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    # Get our visibility results
    mycursor.execute("select UnitTypeID from unit where UnitID in (select UnitID from visibilitychange where ChangeTime = "+ str(frame) + " and VisibilityChangeID = " + str(our_visibility_id) + " and ((UnitTypeID between 60 and 61) or (UnitTypeID between 63 and 88) or (UnitTypeID between 154 and 174)))")
    #print("UnitTypeIDs")
    for i in mycursor:
        #print(i)
        one = re.findall(digit_pattern, str(i))
        our_units_array[int(one[0])] += 1
    return our_units_array

def return_unit_type_number(unit_id):
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select UnitTypeID from unit where UnitID = " + str(unit_id))
    for i in mycursor:
        one = re.findall(digit_pattern, str(i))
        return str(int(one[0]))


def update_build_array(build_array, our_current_units_array, current_frame, replay_id, player_replay_id):
    new_build = False
    units_array = []
    count = 0
    for i in build_array:
        build_array[count][3] = 1- ((float(build_array[count][1]) - float(current_frame)) / float(build_array[count][4]))
        if i[1] == str(current_frame):
            our_current_units_array[int(i[2])] += 1
            build_array.remove(i)
            #rint("Element Removed -------------")
            #print(build_array)
        count = count + 1
    digit_pattern = re.compile('\d+')
    #mycursor.fetchall()
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select UnitID from event where Frame = " + str(current_frame) + " and ReplayID =" + str(replay_id) + " and EventTypeID = 12 and UnitID in (select UnitID from unit where PlayerReplayID = " + str(player_replay_id) + ")")
    for i in mycursor:
        one = re.findall(digit_pattern, str(i))
        units_array.append(one[0])
   
    for i in units_array:
        
        mycursor.execute("select ChangeVal from attributechange where UnitID = " + str(i) +" and AttributeTypeID = 62 Order by ChangeTime limit 1;")
        temp = []
        for j in mycursor:
            
            one = re.findall(digit_pattern, str(j))
            build_array.append([i,str(int(one[0])+current_frame),return_unit_type_number(i),0, current_frame ])
            temp.append(j)
            new_build = True
        if temp == []:
            
            mycursor.execute("select UnitTypeID from unit where UnitID = " + str(i))
            for q in mycursor:
                one = re.findall(digit_pattern, str(q))
                our_current_units_array[int(one[0])] += 1
            
    return build_array, our_current_units_array, new_build

def convert_to_usable_array(current_array, size_of_new_array):
    array = [0] * size_of_new_array
    for i in current_array:
        #print(i)
        #print(max(float(i[3]), float(array[int(i[2])])))
        array[int(i[2])] = max(float(i[3]), float(array[int(i[2])]))
        #print(array)
    return array

#update_techonology(tech_research_array, our_tech_array, current_frame, replay_id, our_player_replay_id)
def update_upgrades(upgrade_being_researched_array, our_upgrade_array, current_frame, replay_id, player_replay_id):
    
    units_array = []
    count = 0
    for i in upgrade_being_researched_array:
        #print(upgrade_being_researched_array)
        #print(upgrade_being_researched_array[count])
        upgrade_being_researched_array[count][3] = 1- ((float(upgrade_being_researched_array[count][1]) - float(current_frame)) / float(upgrade_being_researched_array[count][4]))
        if i[1] == str(current_frame):
            #print(i)
            
            our_upgrade_array[int(i[2])] += 1
            upgrade_being_researched_array.remove(i)
            #rint("Element Removed -------------")
            #print(build_array)
        
        count = count + 1
    digit_pattern = re.compile('\d+')
    x = 0
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    new_cursor = mydb.cursor()
    new_cursor.execute("USE PVTdb;")
    mycursor.execute("select UnitID from attributechange where ChangeTime = " + str(current_frame) + " and AttributeTypeID = 61 and UnitID in (select UnitID from unit where PlayerReplayID = " + str(player_replay_id) + ")")
    for i in mycursor:
        one = re.findall(digit_pattern, str(i))
        units_array.append(one[0])
   
    for i in units_array:
        
        mycursor.execute("select ChangeVal from attributechange where ChangeVal != 44 and UnitID = " + str(i) +" and AttributeTypeID = 65 Order by ChangeTime limit 1;")
        temp = []
        for j in mycursor:
            # This code is messed up
            one = re.findall(digit_pattern, str(j))
            new_cursor.execute("select ChangeVal from attributechange where ChangeTime = " + str(current_frame) + " and ChangeVal != 61 and UnitID = " + str(i) +" and AttributeTypeID = 61;")
            for q in new_cursor:
                two = re.findall(digit_pattern, str(q))
                #print("----------------------------------------------------------------------")
                #print(two)
                if int(two[0]) > 26:
                    x = int(two[0]) + 1
                else : 
                    x = int(two[0])
                upgrade_being_researched_array.append([i,str(int(one[0])+current_frame),x, 0, current_frame])
            temp.append(j)
           
        if temp == []:
            
            mycursor.execute("select ChangeVal from attributechange where ChangeVal != 44 and ChangeTime = " + str(current_frame) + " and AttributeTypeID = 60 and UnitID = " + str(i))
            for q in mycursor:
                one = re.findall(digit_pattern, str(q))
                
                if int(one[0]) > 26:
                    x = int(one[0]) + 1
                else : 
                    x = int(one[0])
                our_tech_array[x] += 1
    #my_cursor.fetchall()  
    return upgrade_being_researched_array, our_upgrade_array


#update_techonology(tech_research_array, our_tech_array, current_frame, replay_id, our_player_replay_id)
def update_technology(tech_being_researched_array, our_tech_array, current_frame, replay_id, player_replay_id):
    
    units_array = []
    count = 0
    for i in tech_being_researched_array:
        #print(tech_being_researched_array[count])
        #print(tech_being_researched_array)
        tech_being_researched_array[count][3] = 1- ((float(tech_being_researched_array[count][1]) - float(current_frame)) / float(tech_being_researched_array[count][4]))
        if i[1] == str(current_frame):
            #print(i)
            
            our_tech_array[int(i[2])] += 1
            tech_being_researched_array.remove(i)
            #rint("Element Removed -------------")
            #print(build_array)
        
        count = count + 1
    
    digit_pattern = re.compile('\d+')
    x = 0
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    new_cursor = mydb.cursor()
    new_cursor.execute("USE PVTdb;")
    mycursor.execute("select UnitID from attributechange where ChangeTime = " + str(current_frame) + " and AttributeTypeID = 60 and UnitID in (select UnitID from unit where PlayerReplayID = " + str(player_replay_id) + ")")
    for i in mycursor:
        one = re.findall(digit_pattern, str(i))
        units_array.append(one[0])
   
    for i in units_array:
        
        mycursor.execute("select ChangeVal from attributechange where ChangeVal != 44 and UnitID = " + str(i) +" and AttributeTypeID = 64 Order by ChangeTime limit 1;")
        temp = []
        for j in mycursor:
            # This code is messed up
            one = re.findall(digit_pattern, str(j))
            new_cursor.execute("select ChangeVal from attributechange where ChangeTime = " + str(current_frame) + " and ChangeVal != 44 and UnitID = " + str(i) +" and AttributeTypeID = 60;")
            for q in new_cursor:
                two = re.findall(digit_pattern, str(q))
                #print("----------------------------------------------------------------------")
                #print(two)
                if int(two[0]) > 26:
                    x = int(two[0]) + 1
                else : 
                    x = int(two[0])
                tech_being_researched_array.append([i,str(int(one[0])+current_frame),x, 0, int(one[0])])
            temp.append(j)
           
        if temp == []:
            
            mycursor.execute("select ChangeVal from attributechange where ChangeVal != 44 and ChangeTime = " + str(current_frame) + " and AttributeTypeID = 60 and UnitID = " + str(i))
            for q in mycursor:
                one = re.findall(digit_pattern, str(q))
                
                if int(one[0]) > 26:
                    x = int(one[0]) + 1
                else : 
                    x = int(one[0])
                our_tech_array[x] += 1
    #mycursor.fetchall()
    return tech_being_researched_array, our_tech_array


def find_next_item_being_built(replay_id, frame, player_replay_id, frame_limit):
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")

    while frame < frame_limit:
        mycursor.execute("select ChangeVal from attributechange where AttributeTypeID = 60 and ChangeTime = "  +  str(frame) + " and UnitID in (select UnitID from unitgroup where UnitGroupID in (select UnitGroupID from action where PlayerReplayID = " + str(player_replay_id) + " and UnitCommandTypeID = 6) )order by ChangeTime limit 1;")
        array = []
        for i in mycursor:
            #print(i)
            array.append(i)

            if array != [] :
                one = re.findall(digit_pattern, str(i))
                #print(one)
                #print(type(one))
                if int(one[0]) == 4:
                    one = 32
                    return str(int(one))
                elif int(one[0]) == 9:
                    one = 33
                    return str(int(one))
                elif int(one[0]) == 19:
                    one = 34
                    return str(int(one))
                elif int(one[0]) == 20:
                    one = 35
                    return str(int(one))
                elif int(one[0]) == 21:
                    one = 36
                    return str(int(one))
                elif int(one[0]) == 22:
                    one = 37
                    return str(int(one))
                elif int(one[0]) == 23:
                    one = 38
                    return str(int(one))
                elif int(one[0]) == 26:
                    one = 39
                    return str(int(one))
                elif int(one[0]) == 28:
                    one = 40
                    return str(int(one))
                elif int(one[0]) == 31:
                    one = 41
                    return str(int(one))
                

                

        
        mycursor.execute("select ChangeVal from attributechange where AttributeTypeID = 61 and ChangeTime = "  +  str(frame) + " and UnitID in (select UnitID from unitgroup where UnitGroupID in (select UnitGroupID from action where PlayerReplayID = " + str(player_replay_id) + " and UnitCommandTypeID = 7) )order by ChangeTime limit 1;")
        array = []
        for i in mycursor:
            #print(i)
            array.append(i)

            if array != [] :
                one = re.findall(digit_pattern, str(i))
                if int(one[0]) == 5:
                    one = 42
                    return str(int(one))
                elif int(one[0]) == 6:
                    one = 43
                    return str(int(one))
                elif int(one[0]) == 13:
                    one = 44
                    return str(int(one))
                elif int(one[0]) == 14:
                    one = 45
                    return str(int(one))
                elif int(one[0]) == 15:
                    one = 46
                    return str(int(one))
                elif int(one[0]) == 22:
                    one = 47
                    return str(int(one))
                elif int(one[0]) == 33:
                    one = 48
                    return str(int(one))
                elif int(one[0]) == 34:
                    one = 49
                    return str(int(one))
                elif int(one[0]) == 35:
                    one = 50
                    return str(int(one))
                elif int(one[0]) == 36:
                    one = 51
                    return str(int(one))
                elif int(one[0]) == 37:
                    one = 52
                    return str(int(one))
                elif int(one[0]) == 38:
                    one = 53
                    return str(int(one))
                elif int(one[0]) == 39:
                    one = 54
                    return str(int(one))
                elif int(one[0]) == 40:
                    one = 55
                    return str(int(one))
                elif int(one[0]) == 41:
                    one = 56
                    return str(int(one))
                elif int(one[0]) == 42:
                    one = 57
                    return str(int(one))
                elif int(one[0]) == 43:
                    one = 58
                    return str(int(one))
                elif int(one[0]) == 44:
                    one = 59
                    return str(int(one))
                elif int(one[0]) == 47:
                    one = 60
                    return str(int(one))
                elif int(one[0]) == 49:
                    one = 61
                    return str(int(one))
                

        mycursor.execute("select UnitTypeID from unit where UnitID in (select UnitID from event  where EventTypeID = 12 and ReplayID = " + str(replay_id) + " and Frame = " + str(frame) + " and UnitID in(select UnitID from unit where PlayerReplayID= " + str(player_replay_id) + ") ) limit 1")
        array = []
        for i in mycursor:
            #print(i)
            array.append(i)

            if array != [] :
                one = re.findall(digit_pattern, str(i))
                if int(one[0]) == 60:
                    one = 0
                    return str(int(one))
                elif int(one[0]) == 61:
                    one = 1
                    return str(int(one))
                elif int(one[0]) == 63:
                    one = 3
                    return str(int(one))
                elif int(one[0]) == 64:
                    one = 4
                    return str(int(one))
                elif int(one[0]) == 65:
                    one = 5
                    return str(int(one))
                elif int(one[0]) == 66:
                    one = 6
                    return str(int(one))
                elif int(one[0]) == 67:
                    one = 7
                    return str(int(one))
                elif int(one[0]) == 68:
                    one = 8
                    return str(int(one))
                elif int(one[0]) == 69:
                    one = 9
                    return str(int(one))
                elif int(one[0]) == 70:
                    one = 10
                    return str(int(one))
                elif int(one[0]) == 71:
                    one = 11
                    return str(int(one))
                elif int(one[0]) == 72:
                    one = 12
                    return str(int(one))
                elif int(one[0]) == 73:
                    one = 13
                    return str(int(one))
                elif int(one[0]) == 83:
                    one = 14
                    return str(int(one))
                elif int(one[0]) == 84:
                    one = 15
                    return str(int(one))
                elif int(one[0]) == 85:
                    one = 16
                    return str(int(one))
                elif int(one[0]) == 154:
                    one = 17
                    return str(int(one))
                elif int(one[0]) == 155:
                    one = 18
                    return str(int(one))
                elif int(one[0]) == 156:
                    one = 19
                    return str(int(one))
                elif int(one[0]) == 157:
                    one = 20
                    return str(int(one))
                elif int(one[0]) == 159:
                    one = 22
                    return str(int(one))
                elif int(one[0]) == 160:
                    one = 23
                    return str(int(one))
                elif int(one[0]) == 162:
                    one = 24
                    return str(int(one))
                elif int(one[0]) == 163:
                    one = 25
                    return str(int(one))
                elif int(one[0]) == 164:
                    one = 26
                    return str(int(one))
                elif int(one[0]) == 165:
                    one = 27
                    return str(int(one))
                elif int(one[0]) == 166:
                    one = 28
                    return str(int(one))
                elif int(one[0]) == 167:
                    one = 29
                    return str(int(one))
                elif int(one[0]) == 169:
                    one = 30
                    return str(int(one))
                elif int(one[0]) == 170:
                    one = 31
                    return str(int(one))
                elif int(one[0]) == 171:
                    one = 21
                    return str(int(one))
                elif int(one[0]) == 172:
                    one = 2
                    return str(int(one))


                

        frame = frame + 1
    return None

def should_event_be_triggered(new_build, unit_destroyed, unit_observed):#replay_id, frame, player_replay_id):
    # mycursor = mydb.cursor()
    # mycursor.execute("USE PVTdb;")
    # mycursor.execute("select * from unit where UnitID in (select UnitID from event where Frame = " + str(frame) + " and ReplayID =" + str(replay_id) + " and EventTypeID = 12 and UnitID in (select UnitID from unit where PlayerReplayID = " + str(player_replay_id) + "))")
    
    # array = []
    # for i in mycursor:
    #     print(i)
    #     array.append(i)

    # if array != [] :
    #     return True
    # else : 
    #     return False

    if new_build == True :
        #print("Event triggered because build")
        return True
    elif unit_destroyed == True:
        #print("Event triggered because Destruction")
        return True
    elif unit_observed == True:
        #print("Event triggered because Observation")
        return True
    else:
        return False

def check_if_units_destroyed(our_units_array, frame, player_replay_id, replay_id):
    #print("Iin")
    unit_destroyed_status = False
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select UnitTypeID from unit where UnitID in (select UnitID from event where Frame = " + str(frame) + " and ReplayID =" + str(replay_id) + " and EventTypeID = 13 and UnitID in (select UnitID from unit where PlayerReplayID = " + str(player_replay_id) + "))")
    for i in mycursor:
        #print("--------------------------------------------------")
        #print(our_units_array)
        one = re.findall(digit_pattern, str(i))
        our_units_array[int(one[0])] = our_units_array[int(one[0])] -  1
        unit_destroyed_status = True
        #print(our_units_array)
    
    return our_units_array, unit_destroyed_status

def enemy_units_observed(replay_id, frame, player_visibility_id, opp_replay_id, opp_units_array, already_seen_units):
    #print("here")
    units_to_process = []
    units_observed_status = False
    one = []
    digit_pattern = re.compile('\d+')
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select UnitID from unit where PlayerReplayID = " + str(opp_replay_id) + " and UnitID in (select UnitID from visibilitychange where ChangeTime = " + str(frame) + " and ViewerID = "  + str(player_visibility_id) + ")")
    for i in mycursor:
        one = re.findall(digit_pattern, str(i))
        already_in_list = False
        for j in already_seen_units:
            if int(one[0]) == int(j):
                already_in_list = True
        if already_in_list == False :
            already_seen_units.append(one[0])
            units_to_process.append(one[0])
    if units_to_process != []:
        units_observed_status = True
        for j in units_to_process:
            mycursor.execute("select UnitTypeID from unit where UnitID = " + str(j))
            for i in mycursor:    
                one = re.findall(digit_pattern, str(i))
                opp_units_array[int(one[0])] += 1
    return opp_units_array, already_seen_units, units_observed_status
     

def create_events_for_specific_replay(replay_id, event_array):
    # Create the initial arrays    
    opp_units_array=[0] * 228 
  
    our_units_array=[0] * 228
    our_tech_array = [0] * 48
    our_upgrades_array = [0] * 56
    build_array = []
    current_frame = 0
    #event_array = []
    already_seen_units = []
    tech_research_array = []
    upgrade_research_array = []
    usable_upgrade_research_array = []
    usable_tech_research_array = []

    
    # Get max frames available in this replay
    max_frames = return_max_frame_in_a_replay(replay_id)

     # If max frames are not returned then that replay does not exist. We can skip it
    if max_frames == None:
        print("-------------------------------------------------")
        print("Replay " + str(replay_id) +" doesn't exist")
        return event_array

    # Get visibility IDS
    our_visibility_id, opp_visibility_id = return_player_opponent_viewer_ids(replay_id)
    #print(our_visibility_id)
    #print(opp_visibility_id)
    if our_visibility_id == None:
        print("-------------------------------------------------")
        print("Replay " + str(replay_id) +" was skipped because of visibility issues")
        return event_array
    if opp_visibility_id == None :
        print("-------------------------------------------------")
        print("Replay " + str(replay_id) +" was skipped because of visibility issues")
        return event_array 

    # Use visibility changes at 0 to determine what units each person starts with. 
    our_units_array = upgrade_array_without_triggering_event(our_units_array, our_tech_array, our_upgrades_array, replay_id, 0, our_visibility_id, opp_visibility_id)

    # Get the replay IDs of both players
    our_player_replay_id, opp_player_replay_id = return_player_replay_ids(replay_id)


    # Run through the entire replay frame by frame
    while current_frame < int(max_frames):
        events = False
        #print("1")
        # Update the build status of our troops at every frame
        build_array,our_units_array, new_build_status = update_build_array(build_array,our_units_array, current_frame, replay_id, our_player_replay_id)
        #print("2")
        # Check if we see any enemy troop at this frame. Update the table with their info.
        opp_units_array, already_seen_units, units_observed_status = enemy_units_observed(replay_id, current_frame,  our_visibility_id, opp_player_replay_id, opp_units_array, already_seen_units)
        #print("3")
        # Check to see if any of our units are destroyed. Update table
        our_units_array, unit_destroyed_status = check_if_units_destroyed(our_units_array, current_frame, our_player_replay_id, replay_id)
        #print("4")
        # Update the technology status
        tech_research_array, our_tech_array = update_technology(tech_research_array, our_tech_array, current_frame, replay_id, our_player_replay_id)
        #if tech_research_array != []:
            #print(tech_research_array)
            #print(our_tech_array)
        #print("5")
        upgrade_research_array, our_upgrades_array = update_upgrades(upgrade_research_array, our_upgrades_array, current_frame, replay_id, our_player_replay_id)
        #if upgrade_research_array != []:
           #print(upgrade_research_array)
           #print(our_upgrade_array)

        usable_upgrade_research_array = convert_to_usable_array(upgrade_research_array, 56)
        usable_tech_research_array = convert_to_usable_array(tech_research_array, 48)
        usable_build_array = convert_to_usable_array(build_array, 228)
        #print(usable_build_array)
        #print("This is the usbale upgrade array")
        #print(usable_upgrade_array)
        # Check to see if an event was triggered
        events = should_event_be_triggered(new_build_status, unit_destroyed_status, units_observed_status)
        #print("_-----------------------------")
        #if current_frame == 5:
            #events = True
        #print("Opp Units array")
        #print(opp_units_array)
        #print("already seen units")
       # print(already_seen_units)

        if events == True:
            pair_array = [our_units_array, opp_units_array, our_tech_array, usable_tech_research_array, our_upgrades_array, usable_upgrade_research_array, find_next_item_being_built(replay_id, current_frame, our_player_replay_id,int(max_frames)), current_frame, max_frames, usable_build_array]
            event_array.append(pair_array)
        current_frame +=1

    # Print out the information for this replay
    #print(event_array)
    #print("-------------------------------------------------")
    #print("Replay "+str(replay_id) + ": ")
    #print("Our Replay ID: " + our_player_replay_id)
    #print("Opp Replay ID: " + opp_player_replay_id)
    #print("Our visibility id: " + our_visibility_id)
    #print("Opp visibility id: " + opp_visibility_id)
    #print("Max frames: " + max_frames)
    #print("Final Tech Array : ")
    #print(our_tech_array)
    return event_array

def run():
    print("running")
    replay_id = 100
    #------------
    test = []
    digit_pattern = re.compile('\d+')
    #------------
    # Go through the first 100 replays
    for i in range(10):
        events = []
        #while replay_id < 2300:
        while replay_id < 50 * i:
            print("Replay id is : " + str(replay_id))
            events = create_events_for_specific_replay(replay_id, events)
            replay_id +=1

            # for q in events:
            #     one = re.findall(digit_pattern, str(q))
            #     #print(one)
            #     check = True
            #     for j in test:
            #         #print("One")
            #         #print(one)
            #         #print("j")
            #         #print(j)
            #         if one==j:
            #             #print("Went here")
            #             check= False
            #     if check == True:
            #         test.append(one)
            #         #print(test)
            #         #print("------------------smokes------------------------")
    
        print(test)
        npa = np.asarray(events, dtype=object)

        with open('test_final' + str(i) +'.npy', 'wb') as f:
            np.save(f, npa)

#run()
def test():
    print("Test")
    mycursor = mydb.cursor()
    mycursor.execute("USE PVTdb;")
    mycursor.execute("select distinct ChangeVal from attributechange where AttributeTypeID = 61 and UnitID in (select UnitID from unitgroup where UnitGroupID in (select UnitGroupID from action where PlayerReplayID = 6 and UnitCommandTypeID = 6) );")
    for i in mycursor:
        print(i)
#test()
events = run()
# npa = np.asarray(events)
# print(events)
# print("NPA IS")
# print(npa)
# with open('test.npy', 'wb') as f:

#     np.save(f, npa)
# print("File Written")
# with open('test.npy', 'rb') as f:

#     a = np.load(f, allow_pickle=True)
#     print("File Loaded")
#     print(a)
# select * from unittype where UnitTypeID in (select UnitTypeID from unit where UnitID in (select UnitID from unitgroup where UnitGroupID in (select UnitGroupID from action where UnitCommandTypeID =7)));
# select * from attributechange where UnitID = 1742 and AttributeTypeID between 60 and 70;
# select * from attributechange where AttributetypeID = 65 and UnitID = 1553;