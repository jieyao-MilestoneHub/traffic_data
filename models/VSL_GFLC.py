import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from deap import base, creator, tools, algorithms

# 定義模糊變數
flow = ctrl.Antecedent(np.arange(0, 101, 1), 'flow')
speed = ctrl.Antecedent(np.arange(0, 101, 1), 'speed')
crash_likelihood = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'crash_likelihood')
speed_limit = ctrl.Consequent(np.arange(0, 121, 1), 'speed_limit')

# 定義模糊隸屬函數
flow['low'] = fuzz.trimf(flow.universe, [0, 0, 50])
flow['medium'] = fuzz.trimf(flow.universe, [0, 50, 100])
flow['high'] = fuzz.trimf(flow.universe, [50, 100, 100])

speed['low'] = fuzz.trimf(speed.universe, [0, 0, 50])
speed['medium'] = fuzz.trimf(speed.universe, [0, 50, 100])
speed['high'] = fuzz.trimf(speed.universe, [50, 100, 100])

crash_likelihood['low'] = fuzz.trimf(crash_likelihood.universe, [0, 0, 0.5])
crash_likelihood['medium'] = fuzz.trimf(crash_likelihood.universe, [0, 0.5, 1])
crash_likelihood['high'] = fuzz.trimf(crash_likelihood.universe, [0.5, 1, 1])

speed_limit['low'] = fuzz.trimf(speed_limit.universe, [0, 0, 60])
speed_limit['medium'] = fuzz.trimf(speed_limit.universe, [40, 80, 120])
speed_limit['high'] = fuzz.trimf(speed_limit.universe, [80, 120, 120])

# 定義模糊規則
rule1 = ctrl.Rule(flow['low'] & speed['low'] & crash_likelihood['low'], speed_limit['high'])
rule2 = ctrl.Rule(flow['low'] & speed['medium'] & crash_likelihood['medium'], speed_limit['medium'])
rule3 = ctrl.Rule(flow['low'] & speed['high'] & crash_likelihood['high'], speed_limit['low'])
rule4 = ctrl.Rule(flow['medium'] & speed['low'] & crash_likelihood['low'], speed_limit['high'])
rule5 = ctrl.Rule(flow['medium'] & speed['medium'] & crash_likelihood['medium'], speed_limit['medium'])
rule6 = ctrl.Rule(flow['medium'] & speed['high'] & crash_likelihood['high'], speed_limit['low'])
rule7 = ctrl.Rule(flow['high'] & speed['low'] & crash_likelihood['low'], speed_limit['medium'])
rule8 = ctrl.Rule(flow['high'] & speed['medium'] & crash_likelihood['medium'], speed_limit['low'])
rule9 = ctrl.Rule(flow['high'] & speed['high'] & crash_likelihood['high'], speed_limit['low'])

# 建立控制系統
speed_limit_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
speed_limit_simulation = ctrl.ControlSystemSimulation(speed_limit_ctrl)

# 創建適應度類和個體類
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# 定義個體生成函數
def create_individual():
    individual = []
    for i in range(3): # flow 變數
        individual.extend(np.random.uniform(0, 100, 3).tolist())
    for i in range(3): # speed 變數
        individual.extend(np.random.uniform(0, 100, 3).tolist())
    for i in range(3): # crash_likelihood 變數
        individual.extend(np.random.uniform(0, 1, 3).tolist())
    for i in range(3): # speed_limit 變數
        individual.extend(np.random.uniform(0, 120, 3).tolist())
    return creator.Individual(individual)

# 評估函數
def evaluate(individual):
    # 將個體的值賦給模糊隸屬函數
    flow['low'] = fuzz.trimf(flow.universe, individual[0:3])
    flow['medium'] = fuzz.trimf(flow.universe, individual[3:6])
    flow['high'] = fuzz.trimf(flow.universe, individual[6:9])
    speed['low'] = fuzz.trimf(speed.universe, individual[9:12])
    speed['medium'] = fuzz.trimf(speed.universe, individual[12:15])
    speed['high'] = fuzz.trimf(speed.universe, individual[15:18])
    crash_likelihood['low'] = fuzz.trimf(crash_likelihood.universe, individual[18:21])
    crash_likelihood['medium'] = fuzz.trimf(crash_likelihood.universe, individual[21:24])
    crash_likelihood['high'] = fuzz.trimf(crash_likelihood.universe, individual[24:27])
    speed_limit['low'] = fuzz.trimf(speed_limit.universe, individual[27:30])
    speed_limit['medium'] = fuzz.trimf(speed_limit.universe, individual[30:33])
    speed_limit['high'] = fuzz.trimf(speed_limit.universe, individual[33:36])

    # 建立模糊控制系統
    speed_limit_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
    speed_limit_simulation = ctrl.ControlSystemSimulation(speed_limit_ctrl)

    # 模擬數據
    simulated_data = [
        {'flow': 70, 'speed': 55, 'crash_likelihood': 0.3, 'expected_speed_limit': 80},
        {'flow': 40, 'speed': 30, 'crash_likelihood': 0.1, 'expected_speed_limit': 100},
        {'flow': 90, 'speed': 70, 'crash_likelihood': 0.5, 'expected_speed_limit': 60},
        # 增加更多的模擬數據
    ]

    total_error = 0
    for data in simulated_data:
        speed_limit_simulation.input['flow'] = data['flow']
        speed_limit_simulation.input['speed'] = data['speed']
        speed_limit_simulation.input['crash_likelihood'] = data['crash_likelihood']
        speed_limit_simulation.compute()
        predicted_speed_limit = speed_limit_simulation.output['speed_limit']
        error = abs(predicted_speed_limit - data['expected_speed_limit'])
        total_error += error

    # 計算適應度分數（誤差越小，適應度越高）
    fitness = 1 / (1 + total_error)
    return fitness,

# 定義交叉、變異和選擇操作
toolbox = base.Toolbox()
toolbox.register("individual", create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

# 建立種群
population = toolbox.population(n=100)

# 運行遺傳演算法
ngen = 50
cxpb = 0.5
mutpb = 0.2

algorithms.eaSimple(population, toolbox, cxpb, mutpb, ngen, verbose=True)

# 選擇最優個體
best_individual = tools.selBest(population, 1)[0]

# 將最優個體的值賦給模糊隸屬函數
flow['low'] = fuzz.trimf(flow.universe, best_individual[0:3])
flow['medium'] = fuzz.trimf(flow.universe, best_individual[3:6])
flow['high'] = fuzz.trimf(flow.universe, best_individual[6:9])
speed['low'] = fuzz.trimf(speed.universe, best_individual[9:12])
speed['medium'] = fuzz.trimf(speed.universe, best_individual[12:15])
speed['high'] = fuzz.trimf(speed.universe, best_individual[15:18])
crash_likelihood['low'] = fuzz.trimf(crash_likelihood.universe, best_individual[18:21])
crash_likelihood['medium'] = fuzz.trimf(crash_likelihood.universe, best_individual[21:24])
crash_likelihood['high'] = fuzz.trimf(crash_likelihood.universe, best_individual[24:27])
speed_limit['low'] = fuzz.trimf(speed_limit.universe, best_individual[27:30])
speed_limit['medium'] = fuzz.trimf(speed_limit.universe, best_individual[30:33])
speed_limit['high'] = fuzz.trimf(speed_limit.universe, best_individual[33:36])

# 重新建立控制系統
speed_limit_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
speed_limit_simulation = ctrl.ControlSystemSimulation(speed_limit_ctrl)

# 使用最佳化後的控制器進行控制
flow_value = 70 # 範例值
speed_value = 55 # 範例值
crash_likelihood_value = 0.3 # 範例值

speed_limit_simulation.input['flow'] = flow_value
speed_limit_simulation.input['speed'] = speed_value
speed_limit_simulation.input['crash_likelihood'] = crash_likelihood_value

speed_limit_simulation.compute()
print(speed_limit_simulation.output['speed_limit'])