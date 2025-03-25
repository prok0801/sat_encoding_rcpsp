from psplib import parse




instance = parse("assets/dataset/j30.sm.tgz/j301_1.sm", instance_format="psplib") 


print(instance.resources)
print(instance.projects)
# print(instance.consumptions)
# print(instance.max_time)