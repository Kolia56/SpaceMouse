# open(callback=None, button_callback=None, button_callback_arr=None, set_nonblocking_loop=True, device=None)
#     Open a 3D space navigator device. Makes this device the current active device, which enables the module-level read() and close()
#     calls. For multiple devices, use the read() and close() calls on the returned object instead, and don't use the module-level calls.

#     Parameters:
#         callback: If callback is provided, it is called on each HID update with a copy of the current state namedtuple
#         dof_callback: If dof_callback is provided, it is called only on DOF state changes with the argument (state).
#         button_callback: If button_callback is provided, it is called on each button push, with the arguments (state_tuple, button_state)
#         device: name of device to open, as a string like "SpaceNavigator". Must be one of the values in `supported_devices`.
#                 If `None`, chooses the first supported device found.
#     Returns:
#         Device object if the device was opened successfully
#         None if the device could not be opened

# read()              Return a namedtuple giving the current device state (t,x,y,z,roll,pitch,yaw,button)
# close()             Close the connection to the current device, if it is open
# list_devices()      Return a list of supported devices found, or an empty list if none found


# dev.open()          Opens the connection (this is always called by the module-level open command,
#                     so you should not need to use it unless you have called close())
# dev.read()          Return the state of the device as namedtuple [t,x,y,z,roll,pitch,yaw,button]
# dev.close()         Close this device

import pyspacemouse
from paho.mqtt import client as mqtt_client
import time

broker = 'xxx.xxx.xxx.xxx'
port = 1883
client_id = 'b91ea0a9-e0f1-425d-b70d-2c560457367f'# f'python-mqtt-{random.randint(0, 1000)}'
topic = "spacemouse/"
tick=0

def button_0(state, buttons, pressed_buttons):
    print("Button:", pressed_buttons)

def button_0_1(state, buttons, pressed_buttons):
    print("Buttons:", pressed_buttons)

def someButton(state, buttons):
    print("Left button - ", buttons[0] , "right button - ", buttons[14] )

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, subtopic, data):
    result = client.publish(topic+subtopic, data)
    # result: [0, 1]
    status = result[0]
    if status != 0:
#        print(f"Sent `{data}` to topic `{topic+subtopic}`")
#    else:
        print(f"Failed to send message to topic {topic+subtopic}")

def send2MQTT(state):
    global tick
    subtopic = "data"
#    print("t=" + str(state.t)) # event time
#    print("x=" + str(state.x)) # position on the plane
#    print("y=" + str(state.y)) # position on the plane
#    print("z=" + str(state.z)) # push [0,-1]
#    print("roll=" + str(state.roll)) # left / right [-1, 1]
#    print("pitch=" + str(state.pitch)) # forward / backward [-1, 1]
#    print("yaw=" + str(state.yaw)) # rotation clockwise / anticlockwise  [-1, 1]
    if state.t - tick > 0.05: # decrease sensitivity
        if abs(state.yaw) > 0.1 or abs(state.z) >= 0.1 or abs(state.pitch) > 0.1 or abs(state.roll) > 0.1: 
            tick = state.t
            pitch = round(state.pitch,1)
            yaw = round(state.yaw,1)
            roll = round(state.roll,1)
            z= round(state.z,1)
            msg = '{"yaw":' + str(yaw) + ',"z":' + str(z) + ',"roll":' + str(roll) + ',"pitch":' + str(pitch) +'}'
#            print(msg)
            publish(client, subtopic, msg)
        elif state.z == 0:
            tick = state.t
            z= state.z
            msg = '{"yaw":' + "99" + ',"z":' + str(z) + ',"roll":' + "99" + ',"pitch":' + "99" +'}'
#            print("MQTT-1 " + msg)            
            publish(client, subtopic, msg)        

def send2MQTTbutton(state, buttons):
    subtopic = "buttons"
    msg = '{"button_left":' + str(buttons[0]) + ',"button_right":' + str(buttons[14]) +'}'
#    print(msg)
    publish(client, subtopic, msg)    

def callback():
    button_arr = [pyspacemouse.ButtonCallback(0, button_0),
                  pyspacemouse.ButtonCallback([1], lambda state, buttons, pressed_buttons: print("Button: 1")),
                  pyspacemouse.ButtonCallback([0, 1], button_0_1), ]
    # success = pyspacemouse.open(dof_callback=pyspacemouse.print_state, button_callback=someButton,
    #                             button_callback_arr=button_arr, device="3Dconnexion Universal Receiver", DeviceNumber=3)
    # success = pyspacemouse.open(dof_callback=pyspacemouse.print_state, button_callback=someButton,
    #                             button_callback_arr=button_arr)    
    success = pyspacemouse.open(dof_callback=send2MQTT, button_callback=send2MQTTbutton,
                            button_callback_arr="", device="3Dconnexion Universal Receiver", DeviceNumber=3)
    if success:
        while True:
            state= pyspacemouse.read()
if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    callback()
  
