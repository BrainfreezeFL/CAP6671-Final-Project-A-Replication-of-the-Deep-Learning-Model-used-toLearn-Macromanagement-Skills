from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
import numpy as np

unit_repo = UnitRepository()
start_units = np.zeros(len(unit_repo.units)).astype(int)

with open('SQL/test_smaller_scale_build_percent_included1.npy', 'rb') as f:

    a = np.load(f, allow_pickle=True)

with open('SQL/test_smaller_scale_build_percent_included2.npy', 'rb') as f:

    b = np.load(f, allow_pickle=True)
    
with open('SQL/test_smaller_scale_build_percent_included3.npy', 'rb') as f:

    c = np.load(f, allow_pickle=True)
with open('SQL/test_smaller_scale_build_percent_included4.npy', 'rb') as f:

    d = np.load(f, allow_pickle=True)
with open('SQL/test_smaller_scale_build_percent_included5.npy', 'rb') as f:

    e = np.load(f, allow_pickle=True)
with open('SQL/test_smaller_scale_build_percent_included6.npy', 'rb') as f:

    j = np.load(f, allow_pickle=True)
with open('SQL/test_smaller_scale_build_percent_included7.npy', 'rb') as f:

    g = np.load(f, allow_pickle=True)
with open('SQL/test_smaller_scale_build_percent_included8.npy', 'rb') as f:

    h = np.load(f, allow_pickle=True)
with open('SQL/test_final1.npy', 'rb') as f:

    r = np.load(f, allow_pickle=True)
with open('SQL/test_final2.npy', 'rb') as f:

    s = np.load(f, allow_pickle=True)
with open('SQL/test_final_1_3.npy', 'rb') as f:

    t = np.load(f, allow_pickle=True)
with open('SQL/test_final_1_4.npy', 'rb') as f:

    u = np.load(f, allow_pickle=True)
with open('SQL/test_final_1_5.npy', 'rb') as f:

    v = np.load(f, allow_pickle=True)
with open('SQL/test_final_1_6.npy', 'rb') as f:

    xx = np.load(f, allow_pickle=True)
with open('SQL/test_final7.npy', 'rb') as f:

    y = np.load(f, allow_pickle=True)
with open('SQL/test_final8.npy', 'rb') as f:

    yy = np.load(f, allow_pickle=True)
    

# Create Forward Model
forward_model = ForwardModel(verbose=True)
vectors = []
next_build = []
z = [r,s,t,u,v,xx,y,yy]#a,b,c,d,e,j,g,h,
count = 0
for q in z:
    #ount = count + 1
    #print(count)

    print("Starting New One")
    for i in q:
        our_units = i[0]
        build_construction = i[9]

        #for g in our_units:
        #print(len(unit_repo.techs))
        own_units_construction = [0] * (len(unit_repo.units))
        for x in range(len(build_construction) -1):
            own_units_construction[x] = [build_construction[x]]
        research_techs = [0] * (len(unit_repo.techs ) + 1 )
        research_upgrades = [0] * (len(unit_repo.upgrades) + 1)
        #print(research_techs)
        #print("Our units")
        #print(our_units)
        opp_units = i[1]
        #print("Opp units")
        #print(opp_units)
        tech_construction =i[3]
        #print(len(tech_construction))
        for x in range(len(tech_construction)-1):
            #print(x)
            research_techs[x] = [tech_construction[x]]
        #print("Tech Under Construction")
        #print(research_techs)
        upgrade_construction = i[5]
        for x in range(len(upgrade_construction)):
            #print(x)
            research_upgrades[x] = [upgrade_construction[x]]
        #print("Upgrades under Construction")
        #print(research_upgrades)
        our_techs = i[2]
        our_upgrades = i[4]
        #print("One")
        apple = GameState(Race.PROTOSS, Race.TERRAN, list(our_units), list(opp_units),own_units_under_construction = [],own_techs_under_construction=list(research_techs),own_upgrades_under_construction=list(research_upgrades), own_techs=list(our_techs), own_upgrades=list(our_upgrades), frame=i[7])
        #print("Two")
        test = GameState.to_vector(apple, include_in_production = True, include_in_progress = True)
        #print(len(test))
        if test != None:
            if i[6] !=None:
                next_build.append(i[6])
                vectors.append(test)

with open('test_vectors_final.npy', 'wb') as f:
   np.save(f, vectors)

with open('test_next_final.npy', 'wb') as f:
   np.save(f, next_build)

with open('test_next_final.npy', 'rb') as f:

     a = np.load(f, allow_pickle=True)

print(a)
print(len(a))
