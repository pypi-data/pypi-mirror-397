import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rshub import load_file 
from rshub import submit_jobs
import numpy as np
import time

token = 'Enter Your token here'
# Change your task name or project name every time you run a new job
project_name = 'Demo'
task_name = 'AIEM'

# ============== CHANGE YOUR INPUT PARAMETERS HERE ==============
# ====== Parameters not define will be set to default values ======
# Step 1: Define Scenario flag
# Step 1: Define Scenario flag
# 'soil: Bare soil
# 'snow: Snow
# 'veg: Vegetation covered soil
scenario_flag = 'soil'

# Step 2: Define observation description
# 1) Observation mode
# 'bs': Active (Backscatter)
# 'tb': Passive (Brightness temperature)
output_var1 = 'sigma' # for soil model, both active and passive results will be outputed; Use this flag to retrieve results

# 2) Observation characteristics
fGHz = 1.26


# Step 3: Define Algorithm flag
algorithm = 'aiem'

# Step 4: Describe your scenario (Demo shows 3-layer snow)
theta_i_deg = [10,20,30,40,50,60] #incident angle in degree.
theta_s_deg = 3 # scattering angle in degree
phi_s_deg = 12.2034 # scattering azimuth angle in deg while  incident azimuth angle is 0 degree
phi_i_deg = 0 # incident azimuth angle
kl = 0.2955 # normalized surface correlation length multiplies by wave number k.
ks = 0.2955 # normalized surface rms height multiplies by wave number k
perm_soil_r = 10.0257 # the real part of surface relative dielectric constant
perm_soil_i = 1.1068 # the imaginary part of surface relative dielectric constant
rough_type = 2 # 1 Gaussian; 2 exponential; 3 transformed exponential correlation (1.5-powe

while True:
    result=submit_jobs.check_completion(token, project_name, task_name)
    status = result.get("task_status", None)  # safe access

    print(f"Status: {status}")

    if status == "completed":
        print("Job completed. Moving to next step...")
        break
    
    if status is None:
        data = {
            'scenario_flag': scenario_flag,
            'output_var': output_var1,'fGHz': fGHz,
            'algorithm':algorithm,
            #'h': h,'Ts':Ts,'Tg':Tg,
            #'epsr_ice_re':epsr_ice_re,'epsr_ice_im':epsr_ice_im,
            'theta_i_deg':theta_i_deg,'theta_s_deg':theta_s_deg,'phi_s_deg':phi_s_deg,'phi_i_deg':phi_i_deg,'kl':kl,
            'ks':ks,'perm_soil_r':perm_soil_r,'perm_soil_i':perm_soil_i,'rough_type':rough_type,
            'project_name':project_name,
            'task_name':task_name,
            'token': token,
            'force_update_flag':1 # force replace existing task 
        }
        result1=submit_jobs.run(data)

    # If not completed, wait 30 seconds
    time.sleep(30)

data = load_file(token, project_name, task_name,scenario_flag=scenario_flag,algorithm=algorithm,output_var=output_var1)
# data_multi = data.load_error_message()
data_multi = data.list_files()
print(data_multi[0])

output = data.load_outputs(data_multi[0])
print(output)
