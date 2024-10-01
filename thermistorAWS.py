import ADC0832
import time
import math
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json

def init():
    ADC0832.setup()

def resistance_to_temperature(Rt):
    BETA = 3950
    T0 = 298.15
    R0 = 10000
    T = 1 / (1 / T0 + (1 / BETA) * math.log(Rt / R0))
    T_celsius = T - 273.15
    return T_celsius

def loop():
    while True:
        res = ADC0832.getADC(0)
        Vr = 3.3 * float(res) / 255
        Rt = 10000 * Vr / (3.3 - Vr)
        
        Cel = resistance_to_temperature(Rt)
        Fah = Cel * 1.8 + 32
        
        print('Temperature: %.2f°C / %.2f°F' % (Cel, Fah))
        
        # Send temperature data via MQTT
        payload = json.dumps({"temperature": Cel, "humidity": 50})  # Update humidity as needed
        myMQTTClient.publish(config.TOPIC, payload, 1)
        
        time.sleep(2)

if __name__ == '__main__':
    # MQTT setup
    myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
    myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
    myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)
    myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
    myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)

    # Connect to MQTT Host
    if myMQTTClient.connect():
        print('AWS connection succeeded')

    # Initialize ADC
    init()
    
    # Start the loop to read temperatures and publish
    try:
        loop()
    except KeyboardInterrupt:
        ADC0832.destroy()
        print('The end!')
