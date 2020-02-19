from enum import Enum, unique
import socket, time
import http.client as httplib

class RemoToMeboConverter:
    messageCount = 0

    def _new_cmd(self):
        result = "!" + self._to_base64(self.messageCount & 63)
        self.messageCount += 1
        return result

    @staticmethod
    def _to_base64(val):
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"[val & 63]

    @staticmethod
    def _encode_base64(val, chars_count):
        result = ""
        for i in range(0, chars_count):
            result += RemoToMeboConverter._to_base64(val >> (i * 6))
        return result

    @staticmethod
    def _encode_speed(speed):
        return RemoToMeboConverter._encode_base64(speed, 2)

    def _command_string(self, cmd, para):
        MeboCmd = MeboCommands 
        enc_spd = self._encode_speed 
        new_cmd = self._new_cmd 
 
        if cmd == MeboCmd.READERS:                 return "READERS=?"
        elif cmd == MeboCmd.FACTORY:               return "P" 
        elif cmd == MeboCmd.BAT:                   return "BAT=?"

        elif cmd == MeboCmd.LIGHT_ON:              return new_cmd() + "RAAAAAAAVd"
        elif cmd == MeboCmd.LIGHT_OFF:             return new_cmd() + "RAAAAAAAVc"
 
        elif cmd == MeboCmd.WHEEL_LEFT_FORWARD:    return new_cmd() + "F" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_LEFT_BACKWARD:   return new_cmd() + "F" + enc_spd(-para)
        elif cmd == MeboCmd.WHEEL_RIGHT_FORWARD:   return new_cmd() + "E" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_RIGHT_BACKWARD:  return new_cmd() + "E" + enc_spd(-para)
        elif cmd == MeboCmd.WHEEL_BOTH_STOP:       return new_cmd() + "B"
 
        elif cmd == MeboCmd.ARM_UP:                return new_cmd() + "G" + enc_spd(para)
        elif cmd == MeboCmd.ARM_DOWN:              return new_cmd() + "G" + enc_spd(-para)
        elif cmd == MeboCmd.ARM_POSITION:          return new_cmd() + "K" + enc_spd(para)
        elif cmd == MeboCmd.ARM_STOP:              return new_cmd() + "CEAA"
        elif cmd == MeboCmd.ARM_QUERY:             return "ARM=?"
 
        elif cmd == MeboCmd.WRIST_UD_UP:           return new_cmd() + "H" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_UD_DOWN:         return new_cmd() + "H" + enc_spd(-para)
        elif cmd == MeboCmd.WRIST_UD_POSITION:     return new_cmd() + "L" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_UD_STOP:         return new_cmd() + "CIAA"
        elif cmd == MeboCmd.WRIST_UD_QUERY:        return "WRIST_UD=?"
 
        elif cmd == MeboCmd.WRIST_ROTATE_LEFT:     return new_cmd() + "I" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_ROTATE_RIGHT:    return new_cmd() + "I" + enc_spd(-para)
        elif cmd == MeboCmd.WRIST_ROTATE_POSITION: return new_cmd() + "M" + enc_spd(para)
        elif cmd == MeboCmd.WRIST_ROTATE_STOP:     return new_cmd() + "CQAA"
        elif cmd == MeboCmd.WRIST_ROTATE_QUERY:    return "WRIST_ROTATE=?"

        elif cmd == MeboCmd.CLAW_POSITION:         return new_cmd() + "N" + enc_spd(para)
        elif cmd == MeboCmd.CLAW_STOP:             return new_cmd() + "CgAA"
        elif cmd == MeboCmd.CLAW_QUERY:            return "CLAW=?"

        elif cmd == MeboCmd.CAL_ARM:               return new_cmd() + "DE"
        elif cmd == MeboCmd.CAL_WRIST_UD:          return new_cmd() + "DI"
        elif cmd == MeboCmd.CAL_WRIST_ROTATE:      return new_cmd() + "DQ"
        elif cmd == MeboCmd.CAL_CLAW:              return new_cmd() + "Dg"
        elif cmd == MeboCmd.CAL_ALL:               return new_cmd() + "D_"

        elif cmd == MeboCmd.VERSION_QUERY:         return "VER=?"
        elif cmd == MeboCmd.REBOOT_CMD:            return new_cmd() + "DE"
        elif cmd == MeboCmd.JOINT_SPEED:           return ""

        elif cmd == MeboCmd.SET_REG:               return ""
        elif cmd == MeboCmd.QUERY_REG:             return "REG" + str(para / 100 % 10) + str(para / 10 % 10) + str(para % 10) + "=?"
        elif cmd == MeboCmd.SAVE_REG:              return "REG=FLUSH"
                    
        elif cmd == MeboCmd.WHEEL_LEFT_SPEED:      return new_cmd() + "F" + enc_spd(para)
        elif cmd == MeboCmd.WHEEL_RIGHT_SPEED:     return new_cmd() + "E" + enc_spd(para)

        elif cmd == MeboCmd.QUERY_EVENT:           return "*"
        else:                                      return ""

    def _generate_single_command(self, number, command, parameter):
        cmd_str = self._command_string(command, parameter)
        return "command" + str(number) + "=mebolink_message_send(" + cmd_str + ")"

    def _generate_message(self, *commands):
        query = "?"
        for i, command in enumerate(commands):
            query += self._generate_single_command(i + 1, command["command"], command["parameter"])
            if i < len(commands) - 1:
                query += "&"
        return query

    def _remo_to_mebo_command(self, cmd, param):

        if type(cmd) is str:
            cmd = RemoCommands(cmd)
        print(cmd)
        mebo_commands = remo_to_mebo_lookup[cmd]
        command_list = []
        for command in mebo_commands:
            command_list.append({
                "command": command,
                "parameter": param
            })
        
        return command_list

    def convert(self, *remo_commands):
        commands = []
        for remo_command in remo_commands:
            commands.extend(self._remo_to_mebo_command(remo_command["command"], remo_command["parameter"]))
        return self._generate_message(*commands)

#TODO maybe remove? Do we really need this?
@unique
class RemoCommands(Enum):
    F = "F"
    B = "B"
    L = "L"
    R = "R"
    
    AU = "AU"
    AD = "AD"
    WU = "WU"
    WD = "WD"
    RL = "RL"
    RR = "RR"

    OI = "OI"
    CI = "CI"

    O = "O"
    C = "C"

    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    
    LY = "LY"
    LN = "LN"

#TODO hook up to config?
class MeboConstants:
    MOVEMENT_SPEED       = 50
    TURNING_SPEED        = 50
    ARM_SPEED            = 100
    WRIST_UD_SPEED       = 100
    WRIST_ROTATION_SPEED = 100
    TURNINGSPEEDS1 = 20
    TURNINGSPEEDS2 = 35
    TURNINGSPEEDS3 = 50

    CLAW_INCREMENT = 10

    CLAW_CLOSE_POSITION = 100
    CLAW_OPEN_POSITION  = 30

    COMMAND_DURATION = 0.5

    MEBO_IP_ADDRESSE = "192.168.99.1"

    LIGHT_ON = 100
    LIGHT_OFF = 100

@unique
class MeboCommands(Enum):
    READERS = "READERS"
    FACTORY = "FACTORY"
    BAT = "BAT"
    
    WHEEL_LEFT_FORWARD = "WHEEL_LEFT_FORWARD"
    WHEEL_LEFT_BACKWARD = "WHEEL_LEFT_BACKWARD"
    WHEEL_RIGHT_FORWARD = "WHEEL_RIGHT_FORWARD"
    WHEEL_RIGHT_BACKWARD = "WHEEL_RIGHT_BACKWARD"
    WHEEL_BOTH_STOP = "WHEEL_BOTH_STOP"

    ARM_UP = "ARM_UP"
    ARM_DOWN = "ARM_DOWN"
    ARM_POSITION = "ARM_POSITION"
    ARM_STOP = "ARM_STOP"
    ARM_QUERY = "ARM_QUERY"

    WRIST_UD_UP = "WRIST_UD_UP"
    WRIST_UD_DOWN = "WRIST_UD_DOWN"
    WRIST_UD_POSITION = "WRIST_UD_POSITION"
    WRIST_UD_STOP = "WRIST_UD_STOP"
    WRIST_UD_QUERY = "WRIST_UD_QUERY"

    WRIST_ROTATE_LEFT = "WRIST_ROTATE_LEFT"
    WRIST_ROTATE_RIGHT = "WRIST_ROTATE_RIGHT"
    WRIST_ROTATE_POSITION = "WRIST_ROTATE_POSITION"
    WRIST_ROTATE_STOP = "WRIST_ROTATE_STOP"
    WRIST_ROTATE_QUERY = "WRIST_ROTATE_QUERY"

    CLAW_POSITION = "CLAW_POSITION"
    CLAW_STOP = "CLAW_STOP"
    CLAW_QUERY = "CLAW_QUERY"

    SET_TURNING_SPEED_1 = "SET_TURNING_SPEED_1"
    SET_TURNING_SPEED_2 = "SET_TURNING_SPEED_2"
    SET_TURNING_SPEED_3 = "SET_TURNING_SPEED_3"
    
    CAL_ARM = "CAL_ARM"
    CAL_WRIST_UD = "CAL_WRIST_UD"
    CAL_WRIST_ROTATE = "CAL_WRIST_ROTATE"
    CAL_CLAW = "CAL_CLAW"
    CAL_ALL = "CAL_ALL"

    VERSION_QUERY = "VERSION_QUERY"
    REBOOT_CMD = "REBOOT_CMD"
    JOINT_SPEED = "JOINT_SPEED"

    SET_REG = "SET_REG"
    QUERY_REG = "QUERY_REG"
    SAVE_REG = "SAVE_REG"

    WHEEL_LEFT_SPEED = "WHEEL_LEFT_SPEED"
    WHEEL_RIGHT_SPEED = "WHEEL_RIGHT_SPEED"

    QUERY_EVENT = "QUERY_EVENT"
    NONE = "NONE"

    LIGHT_ON = "LIGHT_ON"
    LIGHT_OFF = "LIGHT_OFF"


converter = RemoToMeboConverter()

remo_to_mebo_param_lookup = {
    RemoCommands.F: MeboConstants.MOVEMENT_SPEED,
    RemoCommands.B: MeboConstants.MOVEMENT_SPEED,
    RemoCommands.L: MeboConstants.TURNING_SPEED,
    RemoCommands.R: MeboConstants.TURNING_SPEED,

    RemoCommands.AU: MeboConstants.ARM_SPEED,
    RemoCommands.AD: MeboConstants.ARM_SPEED,

    RemoCommands.LY: MeboConstants.LIGHT_ON,
    RemoCommands.LN: MeboConstants.LIGHT_OFF,

    RemoCommands.WU: MeboConstants.WRIST_UD_SPEED,
    RemoCommands.WD: MeboConstants.WRIST_UD_SPEED,

    RemoCommands.RR: MeboConstants.WRIST_ROTATION_SPEED,
    RemoCommands.RL: MeboConstants.WRIST_ROTATION_SPEED,

    RemoCommands.O: MeboConstants.CLAW_OPEN_POSITION,
    RemoCommands.C: MeboConstants.CLAW_CLOSE_POSITION,

    RemoCommands.S1: MeboConstants.TURNINGSPEEDS1,
    RemoCommands.S2: MeboConstants.TURNINGSPEEDS2,
    RemoCommands.S3: MeboConstants.TURNINGSPEEDS3
}

remo_to_mebo_lookup = {
    RemoCommands.F: [
        MeboCommands.WHEEL_LEFT_FORWARD,
        MeboCommands.WHEEL_RIGHT_FORWARD
    ],
    RemoCommands.B: [
        MeboCommands.WHEEL_LEFT_BACKWARD,
        MeboCommands.WHEEL_RIGHT_BACKWARD
    ],
    RemoCommands.L: [
        MeboCommands.WHEEL_LEFT_BACKWARD,
        MeboCommands.WHEEL_RIGHT_FORWARD
    ],
    RemoCommands.R: [
        MeboCommands.WHEEL_LEFT_FORWARD,
        MeboCommands.WHEEL_RIGHT_BACKWARD
    ],
    RemoCommands.LN: [
        MeboCommands.LIGHT_OFF
    ],
    RemoCommands.LY: [
        MeboCommands.LIGHT_ON
    ],
    RemoCommands.AU: [
        MeboCommands.ARM_UP
    ],
    RemoCommands.AD: [
        MeboCommands.ARM_DOWN
    ],
    RemoCommands.WU: [
        MeboCommands.WRIST_UD_UP
    ],
    RemoCommands.WD: [
        MeboCommands.WRIST_UD_DOWN
    ],
    RemoCommands.RL: [
        MeboCommands.WRIST_ROTATE_LEFT
    ],
    RemoCommands.RR: [
        MeboCommands.WRIST_ROTATE_RIGHT
    ],
    RemoCommands.O: [
        MeboCommands.CLAW_POSITION
    ],
    RemoCommands.C: [
        MeboCommands.CLAW_POSITION
    ],
    RemoCommands.OI: [
        MeboCommands.CLAW_POSITION
    ],
    RemoCommands.CI: [
        MeboCommands.CLAW_POSITION
    ],
    RemoCommands.S1: [
        MeboCommands.SET_TURNING_SPEED_1
    ],
    RemoCommands.S2: [
        MeboCommands.SET_TURNING_SPEED_3
    ],
    RemoCommands.S3: [
        MeboCommands.SET_TURNING_SPEED_3
    ]
}

def setup(config):
    print("Mebo Setup")

claw_position = MeboConstants.CLAW_CLOSE_POSITION
def handle_claw_increment(command):
    global claw_position

    if command == "OI":
        claw_position -= MeboConstants.CLAW_INCREMENT
    if command == "CI":
        claw_position += MeboConstants.CLAW_INCREMENT

    if claw_position > MeboConstants.CLAW_CLOSE_POSITION:
        claw_position = MeboConstants.CLAW_CLOSE_POSITION
    if claw_position < MeboConstants.CLAW_OPEN_POSITION:
        claw_position = MeboConstants.CLAW_OPEN_POSITION

    mebo_command = converter.convert({
        "command": command,
        "parameter": claw_position
    })

    try:
        conn = httplib.HTTPConnection(MeboConstants.MEBO_IP_ADDRESSE)
        
        print("\nSTART - sending GET request to: " + str(MeboConstants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n")
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print("Error: %s" % ex)

def handle_speed(command, speed):
    command = command.encode('ascii','ignore')

    if command == "S":
        print("setting speed")
        remo_to_mebo_param_lookup[RemoCommands.F] = speed
        remo_to_mebo_param_lookup[RemoCommands.B] = speed
        return
    if command == "T":
        print("setting turning")
        remo_to_mebo_param_lookup[RemoCommands.L] = speed
        remo_to_mebo_param_lookup[RemoCommands.R] = speed
        return
    
    mebo_command = converter.convert({
        "command": command,
        "parameter": speed
    })

    mebo_command_stop = converter.convert({
        "command": "F",
        "parameter": 0
    }, {
        "command": "AU",
        "parameter": 0
    }, {
        "command": "WU",
        "parameter": 0
    }, {
        "command": "RL",
        "parameter": 0
    })

    try:
        conn = httplib.HTTPConnection(MeboConstants.MEBO_IP_ADDRESSE)
        
        print("\nSTART - sending GET request to: " + str(MeboConstants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n")
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    
        time.sleep(MeboConstants.COMMAND_DURATION)
    
        print("\nSTOP - sending GET request to: " + str(MeboConstants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command_stop + "\n")
        conn.request("GET","/ajax/command.json" + mebo_command_stop)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print("Error: %s" % ex)

meboMSpeedDict = {
	'current':50,
	'home':50,
	'max': 65, #up
	'min': 25 #down
}
meboTSpeedDict = {
	'current':50,
	'home':50,
	'max': 65, #up
	'min': 25 #down
}

def incrementMSpeed(amount):
    meboMSpeedDict['current'] += amount

    if meboMSpeedDict['current'] >= meboMSpeedDict['max']:
        meboMSpeedDict['current'] = meboMSpeedDict['max']
    if meboMSpeedDict['current'] <= meboMSpeedDict['min']:
        meboMSpeedDict['current'] = meboMSpeedDict['min']

    print("increment speed position: ", meboMSpeedDict['current'])
    handle_speed("S", meboMSpeedDict['current'])
    
def incrementTSpeed(amount):
    meboTSpeedDict['current'] += amount

    if meboTSpeedDict['current'] >= meboTSpeedDict['max']:
        meboTSpeedDict['current'] = meboTSpeedDict['max']
    if meboTSpeedDict['current'] <= meboTSpeedDict['min']:
        meboTSpeedDict['current'] = meboTSpeedDict['min']

    print("increment turning position: ", meboTSpeedDict['current'])
    handle_speed("T", meboTSpeedDict['current'])

def move(args):
    command = args['button']['command']
    #command = command.encode('ascii','ignore')
    
    if command == "stop":
        return
    if command == 'SI':
        incrementMSpeed(10)
        time.sleep(0.05)
        return
    if command == 'SD':
        incrementMSpeed(-10)
        time.sleep(0.05)
        return
    if command == 'TI':
        incrementTSpeed(10)
        time.sleep(0.05)
        return
    if command == 'TD':
        incrementTSpeed(-10)
        time.sleep(0.05)
        return
    if command == "OI" or command == "CI":
        handle_claw_increment(command)
        return

    mebo_command = converter.convert({
        "command": command,
        "parameter": remo_to_mebo_param_lookup[RemoCommands(command)]
    })

    mebo_command_stop = converter.convert({
        "command": "F",
        "parameter": 0
    }, {
        "command": "AU",
        "parameter": 0
    }, {
        "command": "WU",
        "parameter": 0
    }, {
        "command": "RL",
        "parameter": 0
    })

    try:
        conn = httplib.HTTPConnection(MeboConstants.MEBO_IP_ADDRESSE)
        
        print("\nSTART - sending GET request to: " + str(MeboConstants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command + "\n")
        conn.request("GET","/ajax/command.json" + mebo_command)
        res = conn.getresponse()
        print(res.status, res.reason)
    
        time.sleep(MeboConstants.COMMAND_DURATION)
    
        print("\nSTOP - sending GET request to: " + str(MeboConstants.MEBO_IP_ADDRESSE) + "/ajax/command.json" + mebo_command_stop + "\n")
        conn.request("GET","/ajax/command.json" + mebo_command_stop)
        res = conn.getresponse()
        print(res.status, res.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print("Error: %s" % ex)