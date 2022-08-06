from dataset import IEEE_CIS

m = IEEE_CIS()
k = m.load_schedule_data()

for ob in k[0]:
    print(ob.batteries)
    print(ob.solars)
