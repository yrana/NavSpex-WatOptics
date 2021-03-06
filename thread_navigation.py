import sys
import os
import time
import RPi.GPIO as GPIO

import Software.WatOptics_firmware.hardware_testing.barcode_scanner.barcode_scanner_video as bsv
import Software.RouteFinding.UserInterfacing.ui_module as ui
import Software.RouteFinding.PathFinding.pf_module as pf
import Software.RouteFinding.Data.symposium_map as d ## this needs to be done based on input

PIN_THOUSAND = 12
PIN_HUNDRED = 16
PIN_TEN = 18
PIN_ONE = 22
PIN_DONE = 24

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(PIN_THOUSAND, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 14 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(PIN_HUNDRED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 16 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(PIN_TEN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 18 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(PIN_ONE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 22 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(PIN_DONE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 24 to be an input pin and set initial value to be pulled low (off)

def DemoButtonInput():
    rooms = []
    rooms.append(4012)
    rooms.append(4013)
    index = -1
    ui.SpeakCommand("Press buttons to select your room and then, press ok ")
    while True:
        if GPIO.input(PIN_THOUSAND) == GPIO.HIGH or GPIO.input(PIN_HUNDRED) == GPIO.HIGH or GPIO.input(PIN_TEN) == GPIO.HIGH or GPIO.input(PIN_ONE) == GPIO.HIGH:
            index = index+1
            if index > len(rooms)-1:
                index = 0
            print("[thread_navigation] asking room: ", rooms[index])
            ui.SpeakCommand(str(rooms[index]))
            time.sleep(0.3)
            
        if GPIO.input(PIN_DONE) == GPIO.HIGH:
            if index < 0:
                index = index+1
            ui.SpeakCommand(" Room Selected, " + str(rooms[index]))
            time.sleep(0.3)
            break;
    return str(rooms[index])
            

def GetButtonInput():
    thousands = 0
    hundreds = 0
    tens = 0
    ones = 0


    while True: # Run forever
        if GPIO.input(PIN_THOUSAND) == GPIO.HIGH:
            
            #roomNumber = 4008
        
            thousands += 1
            if (thousands > 9):
                thousands = 0
            ui.SpeakCommand(str(thousands))
            time.sleep(0.3)
            
        if GPIO.input(PIN_HUNDRED) == GPIO.HIGH:
            
            #roomNumber = 4008
        
            hundreds += 1
            if (hundreds > 9):
                hundreds = 0
            ui.SpeakCommand(str(hundreds))
            time.sleep(0.3)
            
        if GPIO.input(PIN_TEN) == GPIO.HIGH:
            
            #roomNumber = 4037
            
            tens += 1
            if (tens > 9):
                tens = 0
            ui.SpeakCommand(str(tens))
            time.sleep(0.3)
            
        if GPIO.input(PIN_ONE) == GPIO.HIGH:
            
            #roomNumber = 4032
            
            ones += 1
            if (ones > 9):
                ones = 0
            ui.SpeakCommand(str(ones))
            time.sleep(0.3)
        
        if GPIO.input(PIN_DONE) == GPIO.HIGH:
        
            #roomNumber = 4118
        
            print("EXIT BUTTON")
            break
            
    roomNumber = (thousands * 1000) + (hundreds * 100) + (tens * 10) + ones

    thousand_s = str(thousands) + ' '
    hundred_s = str(hundreds) + ' '
    ten_s = str(tens) + ' '
    one_s = str(ones) + ' '

    roomNumber_s = thousand_s + hundred_s + ten_s + one_s

    ui.SpeakCommand("Received Room Number: " + roomNumber_s)
    print(roomNumber)
    return str(roomNumber)

def GetCameraInput(lock):
        
        ui.SpeakCommand("Determining! location, please! stay! steady!")
        camera_return = bsv.scan_barcode()
        # camera_return = "Entrance"
        return camera_return

def IsValid(room):
        if room in d.rooms.keys():
                return True
        else:
                return False

def ValidateRoom(room):
        s = str(room)
        valid_room = IsValid(s)
        counter = 1
        while not valid_room:
                if counter < 2: 
                        ui.SpeakCommand("Invalid room " + str(s) + ", please enter valid room")
                elif counter < 3:
                        ui.SpeakCommand("Invalid room " + str(s) + ", please enter different room")
                else: 
                       ui.SpeakCommand("Invalid room " + str(s) + ", please reconfirm room and enter")
                s = DemoButtonInput()
                valid_room = IsValid(s)
                
                counter += 1
        return s

def GetCurrentLocation(lock):
        ## 1. Use camera to detect current location
        ## 2. Ask user to input the room
        
        # ui.SpeakCommand("Determining! current! location, please! stay! steady!")
        # with lock:
        #        camera_return = bsv.scan_barcode()
        #camera_return = "-1"
        
        camera_return = GetCameraInput(lock)
        
        print("[thread_navigate] camera", camera_return)

        if camera_return != "-1":
                s = camera_return
        else:
                ui.SpeakCommand("Please enter current room")
                s = ValidateRoom(DemoButtonInput())

        roomNum = d.rooms[s][0]
        return roomNum

def GetDestination():
    e = ValidateRoom(DemoButtonInput())
#     e = "Exit"
    return e, d.rooms[e][0]

 
def thread_navigate(shared_val,lock, tIds, num_steps, imu_direction, obs, camera_bool):
    rerun_astar = False
    keepRunning = 0
    start_prog = False
    while keepRunning < 3:
        ## wait for button to start 
        '''# ------ Insert Code here ----- #'''
        ui.SpeakCommand("Please press OK button to begin")
        
        while start_prog == False:
        # might need to add delay here and in room input for SONAR
            if GPIO.input(PIN_THOUSAND) == GPIO.HIGH or GPIO.input(PIN_HUNDRED) == GPIO.HIGH or GPIO.input(PIN_TEN) == GPIO.HIGH or GPIO.input(PIN_ONE) == GPIO.HIGH or GPIO.input(PIN_DONE) == GPIO.HIGH:
                start_prog = True
        '''# ------ End here ----- #'''

        
        ## Get current location
        camera_bool.value = 1
        start = GetCurrentLocation(lock)
        camera_bool.value = 0

        ## Get destination
        if rerun_astar == False:
            '''# ------ Insert Code here ----- #'''
            ui.SpeakCommand("Please enter destination room")
            #e = "4007"
            e, end = GetDestination()
            '''# ------ End here ----- #'''

        ## Run A* 
        coordinates, _, _ = pf.FindPath(tIds, start, end)
        instructions = pf.GetInstructions(coordinates, d.mapScale*d.strideMen)
        rerun_astar = False ## got new path, astar = false
        direction = True
        required_direction = 0
        imu_direction.value = 0
        obs.value = 0

        for inst in instructions:
                required_direction = inst[0]
                required_steps = inst[1]

                ## send instruction
                if required_direction != 0: ## turn required
                        command = ui.GenerateTurnCommand(inst)
                        print(command)
                        ui.SpeakCommand(command)

                        button_pressed = False
                        while not button_pressed:
                                ## obs detect 
                                if obs.value:
                                        ui.SpeakCommand("Obstacle detected")
                                        obs.value = 0
                                        time.sleep(0.1)

                                if GPIO.input(PIN_DONE) == GPIO.HIGH:
                                        print("DETECTED BUTTON PRESS")
                                        print("IMU direction ", imu_direction.value)
                                        if imu_direction.value == 0: ## we missed the turn
                                                required_direction = 0
                                                button_pressed = True
                                        else:
                                                if imu_direction.value != required_direction:
                                                        ui.SpeakCommand("Incorrect turn. Please turn opposite way and press ok to confirm.")
                                                        button_pressed = False
                                                else:
                                                        imu_direction.value = 0
                                                        required_direction = 0
                                                        button_pressed = True
                                        time.sleep(0.3)

                command = ui.GenerateWalkCommand(inst)
                print(command)
                ui.SpeakCommand(command)

                num_steps.value = 0
                while direction == True and num_steps.value < required_steps:
                        ##  Count Steps, Check direction
                        if obs.value:
                            ui.SpeakCommand("Obstacle detected")
                            obs.value = 0
                            time.sleep(0.2)

                        print("[thread_navigation]: steps required: ", required_steps)
                        print("[thread_navigation]: steps taken:", num_steps.value)
                        time.sleep(0.3)
                        ## Direction = true if moving in the true_direction
                        if required_direction == imu_direction.value:
                                time.sleep(1)
                                direction = True
                                imu_direction.value = 0
                                required_direction = 0

                        '''# ------ End here ----- #'''
                ## Turned the wrong way?
                if direction == False:
                        ## they changed direction, rerun A*
                        rerun_astar = True
                        start_prog = True
                        break
        
        if rerun_astar == True:
                ## ignore the rest of the loop and start over
                keepRunning += 1
                continue

        ## Start camera
        '''# ------ Insert Code here ----- #'''
        ## start camera and detect whether destination reached
        camera_bool.value = 1
        camera_input = GetCameraInput(lock)
        camera_bool.value = 0
        #camera_input = camera_return
        print("destination camera: ", str(camera_input), "destination end ", str(end), "destination e ", str(e))
        if str(camera_input) == str(e):
                ui.SpeakCommand("Destination is infront of you.")
                start_prog = False
        ##'''# ------ End here ----- #'''
        else:
                rerun_astar = True
                start_prog = False
                ui.SpeakCommand("Incorrect Destination, restarting program")
        
        keepRunning += 1