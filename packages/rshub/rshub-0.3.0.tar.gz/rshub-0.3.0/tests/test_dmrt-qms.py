import sys
from pathlib import Path
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rshub import load_file 
from rshub import check_completion
from rshub import run
import numpy as np
import time

token = 'Enter Your token here'
# Change your task name or project name every time you run a new job
project_name = 'Demo'
task_name1 = 'DMRT-QMS Active'
task_name2 = 'DMRT-QMS Passive'

# ============== CHANGE YOUR INPUT PARAMETERS HERE ==============
# ====== Parameters not define will be set to default values ======
# Step 1: Define Scenario flag
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
fGHz = 17.2

#angle=[30, 40, 50] # Incident Angle
angle = np.arange(0,70,5)
angle = angle.tolist()


# Step 3: Define Algorithm flag
# qms: DMRT-QMS; bic: DMRT-BIC
algorithm = 'qms'

# Step 4: Describe your scenario (Demo shows 3-layer snow)
depth=[30,20,7,18] # [cm]
rho=[0.111,0.224,0.189,0.216] # [gmcc]
dia=[0.5/10,1.0/10,2.0/10,3.0/10] # Grain size diameter [cm]
tau=[0.12,0.15,0.25,0.35] # stickness #
Tsnow=[260,260,260,260] # Snow temperature [K]

Tg=270 # Ground Temperature [K]
mv=0.15 # soil moisture
clayfrac=0.3 #clay fraction

# Passive parameters to calculate surface backscattering
rough_model = 1 # option 1: Q/H model
rough_Q = 0.5  # polarization mixing factor, unitless          
rough_H = 0.5 # roughness height factor, unitless # Q = H = 0, means flat bottom surface     

surf_model_setting_passive=[rough_model,rough_Q,rough_H] #'QH'

# Active parameters to calculate surface backscattering
rough_model = 1    # option 1: 'OH', option 2: 'SPM3D'; option 3: 'NMM3D'(not suggested, has limited ranges); 
rough_rms = 0.25 # rough ground rms height, (cm) rms == 0 assumes flat bottom boundary
rough_ratio = 7  # correlation length / rms height

surf_model_setting_active=[rough_model,rough_rms,rough_ratio] #'OH'

while True:
    print(f"test")
    result=check_completion(token, project_name, task_name1)
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
            'depth': depth,'rho':rho,'dia':dia,'tau':tau,'Tsnow':Tsnow,'Tg':Tg,
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
print(data_multi)

output = data.load_outputs(data_multi[1])
print(output)


## Passive
while True:
    result=check_completion(token, project_name, task_name2)
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
            'depth': depth,'rho':rho,'dia':dia,'tau':tau,'Tsnow':Tsnow,'Tg':Tg,
            'mv':mv,'clayfrac':clayfrac,'surf_model_setting':surf_model_setting_active,
            'project_name':project_name,
            'task_name':task_name2,
            'token':token,
            'force_update_flag':1
        }
        result1=run(data2)

    # If not completed, wait 30 seconds
    time.sleep(30)

data = load_file(token, project_name, task_name2,scenario_flag=scenario_flag,algorithm=algorithm,output_var=output_var2)
# data_multi = data.load_error_message()
data_multi = data.list_files()
print(data_multi[1])

output = data.load_outputs(data_multi[1])
print(output)
