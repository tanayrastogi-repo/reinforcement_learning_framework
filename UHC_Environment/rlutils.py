# Pyt
import numpy as np



class Variable:
    def __init__(self, minimum, maximum, res):
        no_of_bin = int((maximum - minimum)/res) + 1
        self.state_space = np.linspace(minimum, maximum, no_of_bin, dtype=np.float).round(decimals=2)
        
    def digitize(self, value):
        val = np.digitize(value, self.state_space, right = True)
        return self.state_space[val]


class State:
    def __init__(self,):
        print("Initializng State")
        # State variables
        self.outdoor_temp      = None
        self.solar_rad         = None
        # self.hvac_heat_energy  = None
        self.zone_air_temp     = None
        # self.zone_people_count = None
        # self.hw_mass_flow_rate = None
        
        # State Space for the variables
        self.outdoor_temp_state_space      = Variable(minimum=-17,maximum=19,  res=5)
        self.solar_rad_state_space         = Variable(minimum=0,  maximum=600, res=100)
        # self.hvac_heat_energy_state_space  = Variable(minimum=0,  maximum=2800,res=200)
        self.zone_air_temp_state_space     = Variable(minimum=18 ,maximum=27,  res=1)
        # self.zone_people_count_state_space = Variable(minimum=0 ,maximum=1 , res=0.25)
        # self.hw_mass_flow_rate_state_space = Variable(minimum=0 ,maximum=0.1 , res=0.05)
        
        # Getting Space State
        self.state_space = self._get_state_space()
        
    def _get_state_space(self, ):
        states = list()        
        for ottemp in self.outdoor_temp_state_space.state_space:
            for solar in self.solar_rad_state_space.state_space:
                # for hvac in self.hvac_heat_energy_state_space.state_space:
                   for airtemp in self.zone_air_temp_state_space.state_space: 
                       # for ppl in self.zone_people_count_state_space.state_space: 
                           # for hw in self.hw_mass_flow_rate_state_space.state_space: 
                               # states.append((ottemp, solar, hvac, airtemp, ppl, hw))
                               states.append((ottemp, solar, airtemp))
        return states
                         
    def update_states(self, observation):
        # Digitize the observation to States
        self.outdoor_temp      = self.outdoor_temp_state_space.digitize(observation[0])
        self.solar_rad         = self.solar_rad_state_space.digitize(observation[1])
        # self.hvac_heat_energy  = self.hvac_heat_energy_state_space.digitize(observation[2])
        self.zone_air_temp     = self.zone_air_temp_state_space.digitize(observation[3])
        # self.zone_people_count = self.zone_people_count_state_space.digitize(observation[4])
        # self.hw_mass_flow_rate = self.hw_mass_flow_rate_state_space.digitize(observation[5])

        

    def get_states(self, ):
        # return (self.outdoor_temp, self.solar_rad, self.hvac_heat_energy, self.zone_air_temp, self.zone_people_count, self.hw_mass_flow_rate)
        return (self.outdoor_temp, self.solar_rad, self.zone_air_temp)

    def __len__(self, ):
        return 6
    
    def __str__(self, ):
        # return "{}, {}, {}, {}, {}, {}".format(self.outdoor_temp, self.solar_rad, self.hvac_heat_energy, self.zone_air_temp, self.zone_people_count, self.hw_mass_flow_rate)
        return "{}, {}, {}".format(self.outdoor_temp, self.solar_rad, self.zone_air_temp)


class Action:
    def __init__(self, res=1, min_temp = 18, max_temp = 22, default = 20):
        print("Initializng Actions")
        # Actions
        self.up = res
        self.none = 0
        self.down = -res
        
        # Temperature Limits
        self.min = min_temp
        self.max = max_temp
        
        # Default Setpoint Temperature
        self.default = default
        
        # Getting Space State
        self.state_space = self._get_state_space()        
                
    def sample(self, ):
        action = np.random.choice([self.up, self.none, self.down])
        return action
    
    def _get_state_space(self, ):
        return np.array([self.up, self.none, self.down])
    
    def __len__(self, ):
        return 1



class Reward:
    def __init__(self, ):
        pass