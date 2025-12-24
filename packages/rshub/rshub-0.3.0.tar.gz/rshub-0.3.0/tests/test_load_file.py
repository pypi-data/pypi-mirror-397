import sys
from pathlib import Path
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rshub import load_file

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

angle = 30

# Step 3: Define Algorithm flag
# qms: DMRT-QMS; bic: DMRT-BIC
algorithm = 'qms'

data = load_file(token, project_name, task_name1,scenario_flag=scenario_flag,algorithm=algorithm,output_var=output_var1)
print(data)
# data_multi = data.load_error_message()
data_multi = data.list_files()
print(data_multi)

# # output = data.load_outputs(data_multi[1])
# # print(output)

# output = data.load_outputs(download_path="/home/server/zjuiEMLab/RSHub/RSHub-core/tools/tests/")
# print(output)
