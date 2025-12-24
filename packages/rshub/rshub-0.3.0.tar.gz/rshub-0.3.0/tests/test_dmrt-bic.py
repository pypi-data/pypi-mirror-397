import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rshub import load_file 
from rshub import submit_jobs
import numpy as np
import time

token = 'Enter Your token here'

# Change your task name or project name every time you run a new job
project_name = 'Demo'
task_name1 = 'DMRT-BIC Active'
task_name2 = 'DMRT-BIC Passive'

# ============== CHANGE YOUR INPUT PARAMETERS HERE ==============
# ====== Parameters not define will be set to default values ======
# Step 1: Define Scenario flag
# 'soil': Bare soil
# 'snow': Snow
# 'veg': Vegetation covered soil
scenario_flag = 'snow'

# Step 2: Define observation description
# 1) Observation mode
# 'bs': Active (Backscatter)
# 'tb': Passive (Brightness temperature)
output_var1 = 'sigma'
output_var2 = 'tb'

# 2) Observation characteristics
fGHz = [10.2, 16.7]

# angle=[30, 40, 50] # Incident Angle
angle = np.arange(0,70,5)
angle = angle.tolist()


# Step 3: Define Algorithm flag
# 'qms': DMRT-QMS; 'bic': DMRT-BIC
algorithm = 'bic'

# Step 4: Describe your scenario (Demo shows 3-layer snow)
depth=[6, 2, 8] # [cm]
rho=[0.108,0.108,0.208] # [gmcc]
zp=[1.2,1.2,1.6] # control size distribution
kc=[7000,7500,5500] #inversely propotional to grain size [m^-1]
Tsnow=[260,262,265] # Snow temperature [K]

Tg=270 # Ground Temperature [K]
mv=0.2 # soil moisture
clayfrac=0.3 #clay fraction

# Passive parameters to calculate surface backscattering
rough_model = 1 # option 1: Q/H model; option 2: Wegmuller and Matzler 1999 model
rough_Q = 0.5  # polarization mixing factor, unitless          
rough_H = 0.5 # roughness height factor, unitless # Q = H = 0, means flat bottom surface     

surf_model_setting_passive=[rough_model,rough_Q,rough_H] #'OH'

# Active parameters to calculate surface backscattering
rough_model = 3    # option 1: 'NMM3D'; option 2: 'SPM3D'; option 3: 'OH'
rough_rms = 0.25 # rough ground rms height, (cm) rms == 0 assumes flat bottom boundary
rough_ratio = 7  # correlation length / rms height

surf_model_setting_active=[rough_model,rough_rms,rough_ratio] #'OH'

while True:
    result=submit_jobs.check_completion(token, project_name, task_name1)
    status = result.get("task_status", None)  # safe access

    print(f"Status: {status}")

    if status == "completed":
        print("Job completed. Moving to next step...")
        break
    
    if status is None:
        data1 = {
            'scenario_flag': scenario_flag, 
            'output_var': output_var1,'fGHz': fGHz,
            'angle':angle,
            'algorithm':algorithm,
            'depth': depth,'rho':rho,'kc':kc,'zp':zp,'Tsnow':Tsnow,'Tg':Tg,
            'mv':mv,'clayfrac':clayfrac,'surf_model_setting':surf_model_setting_active,
            'project_name':project_name,
            'task_name':task_name1,
            'token':token,
            'force_update_flag':1
        }
        result1=submit_jobs.run(data1)

    # If not completed, wait 30 seconds
    time.sleep(30)

data = load_file(token, project_name, task_name1,scenario_flag=scenario_flag,algorithm=algorithm,output_var=output_var1)
# data_multi = data.load_error_message()
data_multi = data.list_files()
print(data_multi[1])

output = data.load_outputs(data_multi[1])
print(output)


## Passive
while True:
    result=submit_jobs.check_completion(token, project_name, task_name2)
    status = result.get("task_status", None)  # safe access

    print(f"Status: {status}")

    if status == "completed":
        print("Job completed. Moving to next step...")
        break
    
    if status is None:
        data2 = {
            'scenario_flag': scenario_flag, 
            'output_var': output_var2,'fGHz': fGHz,
            'angle':angle,
            'algorithm':algorithm,
            'depth': depth,'rho':rho,'kc':kc,'zp':zp,'Tsnow':Tsnow,'Tg':Tg,
            'mv':mv,'clayfrac':clayfrac,'surf_model_setting':surf_model_setting_passive,
            'project_name':project_name,
            'task_name':task_name2,
            'token':token,
            'force_update_flag':1
        }
        result1=submit_jobs.run(data2)

    # If not completed, wait 30 seconds
    time.sleep(30)

data = load_file(token, project_name, task_name2,scenario_flag=scenario_flag,algorithm=algorithm,output_var=output_var2)
# data_multi = data.load_error_message()
data_multi = data.list_files()
print(data_multi[1])

output = data.load_outputs(data_multi[1])
print(output)
