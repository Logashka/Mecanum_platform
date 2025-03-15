from machine import Pin, PWM
import machine
class Motor:

    def __init__(self, direction1_pin: int, direction2_pin: int, power_pin: int, encoder1_pin: int, encoder2_pin: int, stby_pin: int) -> None:
        # direction1_pin, direction2_pin - пины направлений на драйвере | power_pin - ШИМ | encoder1_pin, encoder2_pin - пины энкодера в режиме прерываний | stby - пин включения драйвера

        self.direction1_pin = Pin(direction1_pin, Pin.OUT)
        self.direction2_pin = Pin(direction2_pin, Pin.OUT)
        self.power_pin = PWM(power_pin)
        self.encoder1_pin = Pin(encoder1_pin, Pin.IN, Pin.PULL_DOWN)
        self.encoder1_pin.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.Enc_Handler)
        self.encoder2_pin = Pin(encoder2_pin, Pin.IN, Pin.PULL_DOWN)
        self.encoder2_pin.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.Enc_Handler)
        self.stby_pin = Pin(stby_pin, Pin.OUT)
        
        self.power_pin.freq(1000)
        self.stby_pin.value(1)

        self.enc1_state_old = self.encoder1_pin.value()
        self.enc2_state_old = self.encoder2_pin.value()
        self.last_enc_counter = 0
        self.enc_counter = 0
        self.last_qtr_cntr = 0
        self.qtr_cntr = 0
        self.error = 0 
        self.encoder_delta = 1

        self.dir_reverse_status = False
        self.enc_reverse_status = False


    def Enc_Handler(self, Source):
        # Обработчик прерываний
        #s = str(Source)  #useful for debugging and setup to see which pin triggered interupt
        #print(s[4:6])
            
        enc1_state = self.encoder1_pin.value()  #Capture the current state of both A and B
        enc2_state = self.encoder2_pin.value()
        if enc1_state == self.enc1_state_old and enc2_state == self.enc2_state_old:  #Probably 'bounce" as there was a trigger but no change
            self.error += 1  #add the error event to a variable - may by useful in debugging
        elif (enc1_state == 1 and self.enc2_state_old == 0) or (enc1_state == 0 and self.enc2_state_old == 1):
            # this will be clockwise rotation
            # A   B-old
            # 1 & 0 = CW rotation
            # 0 & 1 = CW rotation
            self.enc_counter += self.encoder_delta  #Increment counter by 1 - counts ALL transitions
            self.qtr_cntr = round(self.enc_counter * 2)  #Calculate a new 1/4 counter value
        elif (enc1_state == 1 and self.enc2_state_old == 1) or (enc1_state == 0 and self.enc2_state_old == 0):
            # this will be counter-clockwise rotation
            # A   B-old
            # 1 & 1 = CCW rotation
            # 0 & 0 = CCW rotation
            self.enc_counter -= self.encoder_delta # Decrement counter by 1 - counts ALL transitions
            self.qtr_cntr = round(self.enc_counter * 2)  #Calculate a new 1/4 counter value
        else:  #if here, there is a combination we don't care about, ignore it, but track it for debugging
            self.error += 1
        self.enc1_state_old = enc1_state     # store the current encoder values as old values to be used as comparison in the next loop
        self.enc2_state_old = enc2_state       
        print(f"Enc_Handler: enc_counter={self.enc_counter}, qtr_cntr={self.qtr_cntr}")  # <--- Проверка данных
    
    def reverse(self, move=False, encoder=False) -> None:
        # move=True инвертирует направление движения двигателя | encoder=True инвертирует направление энкодера
        if move != self.dir_reverse_status:
            self.direction1_pin, self.direction2_pin = self.direction2_pin, self.direction1_pin        
            self.dir_reverse_status = move
        if encoder != self.enc_reverse_status:
            self.encoder_delta *= -1
            self.enc_reverse_status = encoder

    def start(self, power: int) -> None:
        # запуск мотора в процентах мощности
        if power > 0 :
            self.direction1_pin.value(1)
            self.direction2_pin.value(0)
        else:
            self.direction1_pin.value(0)
            self.direction2_pin.value(1)
        
        self.power_pin.duty_u16(int((abs(power) * 65536) / 100))

    def stop(self, type: bool) -> None:
        # остановка мотора | True - жесткае, False - мягкая
        if type:
            self.direction1_pin.value(1)
            self.direction2_pin.value(1)
        else:
            self.direction1_pin.value(0)
            self.direction2_pin.value(0)
        
        self.power_pin.duty_u16(0)

    def get_count(self) -> int:
        #irq_state = machine.disable_irq()  # Отключаем прерывания
        count = self.enc_counter
        #machine.enable_irq(irq_state)  # Включаем обратно
        return count

    
    def reset_count(self) -> None:
        self.last_enc_counter = 0
        self.enc_counter = 0
        self.last_qtr_cntr = 0
        self.qtr_cntr = 0
        self.error = 0         



class MotorA(Motor):
    def __init__(self) -> None:
        # test_motor = Motor(14, 15, 13, 16, 17, 12)
        direction1_pin = 13
        direction2_pin = 14
        power_pin = 15
        encoder1_pin = 26
        encoder2_pin = 22
        stby_pin = 12
        super().__init__(direction1_pin, direction2_pin, power_pin, encoder1_pin, encoder2_pin, stby_pin)



class MotorB(Motor):
    def __init__(self) -> None:
        # test_motor = Motor(14, 15, 13, 16, 17, 12)
        direction1_pin = 10
        direction2_pin = 11
        power_pin = 9
        encoder1_pin = 21
        encoder2_pin = 20
        stby_pin = 12
        super().__init__(direction1_pin, direction2_pin, power_pin, encoder1_pin, encoder2_pin, stby_pin)



class MotorC(Motor):

    def __init__(self) -> None:
        # test_motor = Motor(14, 15, 13, 16, 17, 12)
        direction1_pin = 6
        direction2_pin = 7
        power_pin = 8
        encoder1_pin = 19
        encoder2_pin = 18
        stby_pin = 5
        super().__init__(direction1_pin, direction2_pin, power_pin, encoder1_pin, encoder2_pin, stby_pin)



class MotorD(Motor):
    def __init__(self) -> None:
        # test_motor = Motor(14, 15, 13, 16, 17, 12)
        direction1_pin = 3
        direction2_pin = 4
        power_pin = 2
        encoder1_pin = 17
        encoder2_pin = 16
        stby_pin = 5
        super().__init__(direction1_pin, direction2_pin, power_pin, encoder1_pin, encoder2_pin, stby_pin)
