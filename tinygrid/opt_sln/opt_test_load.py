from tinygrid.dataset import IEEE_CISMixin
import os

o = IEEE_CISMixin._load_schedule_data()
U = o['phase1_instance_large_0.txt']

print(U)