int pwm_pin1 = 9;
int pwm_pin2 = 10;
char val;

void setup() 
{
  Serial.begin(9600);         //Sets the data rate in bits per second (baud) for serial data transmission
  pinMode(pwm_pin1, OUTPUT);
  pinMode(pwm_pin2, OUTPUT);
}


void loop()
{

  while (Serial.available() > 0)
  {
    val = Serial.read();
    Serial.println(val);
    //Serial.print(val);        //Print Value of Incoming_value in Serial monitor
    //Serial.print("\n");        //New line 
  }

  
  if( val == '1') // Off
    {
      analogWrite(pwm_pin1, 0);
      analogWrite(pwm_pin2, 0);
    }
    
    else if(val == '2') // 25%
    {
      analogWrite(pwm_pin1, 43); //This value is "-20" from pwm_pin2 because this wheel spins faster and need to be compensated.
      analogWrite(pwm_pin2, 63);
    }

    else if(val == '3') // 50%
    {
      analogWrite(pwm_pin1, 107); //This value is "-20" from pwm_pin2 because this wheel spins faster and need to be compensated.
      analogWrite(pwm_pin2,127);
    }

    else if(val == '4') // 75%
    {
      analogWrite(pwm_pin1, 171); //This value is "-20" from pwm_pin2 because this wheel spins faster and need to be compensated.
      analogWrite(pwm_pin2, 191);
    }

    else if(val == '5') // 100%
    {
      analogWrite(pwm_pin1, 235); //This value is "-20" from pwm_pin2 because this wheel spins faster and need to be compensated.
      analogWrite(pwm_pin2, 255);
    }                    
}  

