from reader import generate_tab_files
from Empire import run_empire
from scenario_random import generate_random_scenario
from reset_investments import reset_investment_files
from datetime import datetime
import time
import gc
import os
from functools import reduce
from operator import mul



########
##USER##
########

USE_TEMP_DIR = True #True/False
temp_dir = '/mnt/beegfs/users/erlenhor'
version = 'full_model_20_nodes'
NoOfPeriods = 8

        #[spring, summer, fall, peak1, winter, peak2]

H2LoadScale = 1
#initial_branches = 1
name = f'constant_demand'
weekHours = 24*7*2
weeksPerMonth = 1
MaxChargeAndDischargePercentage = 0.05
Season = ['january','february','march','april','may','june','july','august','september','october','november','december']
branch_split_per_season = [3,1,1,1,2,1,1,1,2,1,1,1]
#number_of_branches_per_season = [initial_branches] + [initial_branches * reduce(mul, branch_split_per_season[:i+1]) for i in range(len(branch_split_per_season))]
number_of_branches_per_season = [reduce(mul, branch_split_per_season[:i+1]) for i in range(len(branch_split_per_season))]
number_of_branches = sum(number_of_branches_per_season)

#NoOfScenarios = 1
NoOfRegSeason = 12
lengthRegSeason = weekHours
regular_seasons = ['january','february','march','april','may','june','july','august','september','october','november','december']
NoOfPeakSeason = 0
lengthPeakSeason = 0
discountrate = 0.05
WACC = 0.05
LeapYearsInvestment = 3
solver = "Gurobi" #"Gurobi" #"CPLEX" #"Xpress"
branch_generation = False
EMISSION_CAP = True #False
WRITE_LP = False #True
PICKLE_INSTANCE = False #True
FIX_SAMPLE = True
FLEX_HYDROGEN = False
RENEWABLE_GRID_RULE = False
REDUCED_GEN = True

GREEN_HYDROGEN = True
REFORMER_HYDROGEN = False

#CHANGE THESE:

HYDROGEN_CONSTANT_DEMAND = True

SEASONAL_STORAGE = False










def get_unique_filename(base_path, filename):
    """
    Generates a unique filename. If the given filename already exists, it appends a number to the filename.

    :param base_path: The directory in which to check for the file.
    :param filename: The desired filename.
    :return: A unique filename.
    """
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(base_path, unique_filename)):
        unique_filename = f"{filename}_{counter}"
        counter += 1
    return base_path + unique_filename

#######
##RUN##
#######
# if FLEX_IND is True:
#     ind_str = 'flexible_industry'
# else:
#     ind_str = 'inflexible_industry'

if GREEN_HYDROGEN is True:
    green_str = 'GREEN_HYDROGEN'
else:
    green_str = 'no_GREEN_HYDROGEN' 


workbook_path = 'Data handler/' + version
tab_file_path = 'Data handler/' + version + '/Tab_Files_' + name
data_handler_path = 'Data handler/' + version
branch_data_path = 'Data handler/' + version + '/ScenarioData'
result_file_path = get_unique_filename('Results_2w/',name)

FirstHoursOfRegSeason = [1+lengthRegSeason*i for i in range(NoOfRegSeason)]
FirstHoursOfPeakSeason = []
Period = [i + 1 for i in range(NoOfPeriods)]
#Scenario = ["scenario"+str(i + 1) for i in range(NoOfScenarios)]
peak_seasons = []
Operationalhour = [i + 1 for i in range(weekHours*weeksPerMonth*12)]
HoursOfRegSeason = [(s,h) for s in regular_seasons for h in Operationalhour \
                 if h in list(range(FirstHoursOfRegSeason[regular_seasons.index(s)],
                               FirstHoursOfRegSeason[regular_seasons.index(s)] + lengthRegSeason))]
HoursOfPeakSeason = []
HoursOfSeason = HoursOfRegSeason + HoursOfPeakSeason


# dict_countries = {"AT": "Austria", "BA": "BosniaH", "BE": "Belgium",
#                   "BG": "Bulgaria", "CH": "Switzerland", "CZ": "CzechR",
#                   "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
#                   "ES": "Spain", "FI": "Finland", "FR": "France",
#                   "GB": "GreatBrit.", "GR": "Greece", "HR": "Croatia",
#                   "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
#                   "LT": "Lithuania", "LU": "Luxemb.", "LV": "Latvia",
#                   "MK": "Macedonia", "NL": "Netherlands", "NO": "Norway",
#                   "PL": "Poland", "PT": "Portugal", "RO": "Romania",
#                   "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia",
#                   "SK": "Slovakia", "MF": "MorayFirth", "FF": "FirthofForth",
#                   "DB": "DoggerBank", "HS": "Hornsea", "OD": "OuterDowsing",
#                   "NF": "Norfolk", "EA": "EastAnglia", "BS": "Borssele",
#                   "HK": "HollandseeKust", "HB": "HelgoländerBucht", "NS": "Nordsøen",
#                   "UN": "UtsiraNord", "SN1": "SørligeNordsjøI", "SN2": "SørligeNordsjøII",
#                   "EHGB":"Energyhub Great Britain", "EHNO": "Energyhub Norway",
#                   "EHEU": "Energyhub EU"}


dict_countries = {

    "CZ": "Czechoslovakia",
    "SK": "Czechoslovakia",

    "HU": "Hungary",

    "PL": "Poland",

    "BG": "Balkan", 
    "BA": "Balkan", 
    "RS": "Balkan",
    "MK": "Balkan",
    "SI": "Balkan",
    "HR": "Balkan",

    "RO": "Romania",

    "LU": "Benelux",
    "NL": "Benelux",
    "BS": "Benelux",
    "HK": "Benelux",
    "BE": "Benelux",

    "FR": "France",

    "HB": "Germany",
    "DE": "Germany",


    "CH": "Switzerland-Austria",
    "AT": "Switzerland-Austria",

    "PT": "Portugal",

    "ES": "Spain",

    "IT": "Italy",

    "GR": "Greece",

    "IE": "Ireland",

    "MF": "GreatBrit.",
    "FF": "GreatBrit.",
    "DB": "GreatBrit.",
    "HS": "GreatBrit.",
    "OD": "GreatBrit.",
    "NF": "GreatBrit.",
    "EA": "GreatBrit.",
    "EHEU": "GreatBrit.",
    "EHGB": "GreatBrit.",
    "GB": "GreatBrit.",

    "NO": "Norway",
    "NO1": "Norway",
    "NO2": "Norway",
    "NO3": "Norway",
    "NO4": "Norway",
    "NO5": "Norway",
    "UN": "Norway",
    "SN1": "Norway",
    "SN2": "Norway",
    "EHNO": "Norway",

    "SE": "Sweden",

    "NS": "Denmark",
    "DK": "Denmark",

    "EE": "Baltic",
    "LT": "Baltic",
    "LV": "Baltic",

    "FI": "Finland",
}



representative_countries = {
    "Czechoslovakia": 'SK',
    "Hungary":"HU",
    "Poland":"PL",
    'Balkan': 'BG',
    'Romania': 'RO',
    'Benelux': 'BE',
    'France': 'FR',
    'Germany': 'DE',
    "Switzerland-Austria": "AT",
    'Portugal': 'PT',
    'Spain': 'ES',
    'Italy': 'IT',
    'Greece': 'GR',
    'Ireland': 'IE',
    'GreatBrit.': 'GB',
    'Norway': 'NO3',
    'Sweden': 'SE',
    'Denmark': 'DK',
    'Baltic': 'LT',
    'Finland': 'FI'
}

representative_countries_H2 = {
    "Czechoslovakia": 'SK',
    "Hungary":"HU",
    "Poland":"PL",
    'Balkan': 'BG',
    'Romania': 'RO',
    'Benelux': 'BE',
    'France': 'FR',
    'Germany': 'DE',
    "Switzerland-Austria": "AT",
    'Portugal': 'PT',
    'Spain': 'ES',
    'Italy': 'IT',
    'Greece': 'GR',
    'Ireland': 'IE',
    'GreatBrit.': 'GB',
    'Norway': 'DK',
    'Sweden': 'SE',
    'Denmark': 'DK',
    'Baltic': 'LT',
    'Finland': 'FI'
}

print('++++++++')
print('+EMPIRE+')
print('++++++++')
print('Solver: ' + solver)
print('Scenario Generation: ' + str(branch_generation))
print('++++++++')
print('ID: ' + name)
print('++++++++')
print('Green Hydrogen module: ' + str(GREEN_HYDROGEN))
print('Reformer Hydrogen module: ' + str(REFORMER_HYDROGEN))
print('++++++++')
print('Seasonal Storage: ' + str(SEASONAL_STORAGE))
print('Constant Hydrogen Demand: ' + str(HYDROGEN_CONSTANT_DEMAND))
print('Hydrogen Demand Scale Factor: ' + str(H2LoadScale))
print('++++++++')

all_branches = list(range(1,number_of_branches+1))

branches_of_season = []

for nr in number_of_branches_per_season:
    branches_of_season.append(all_branches[:nr])
    all_branches = all_branches[nr:]
print(branches_of_season)

all_branches = list(range(1,number_of_branches+1))

parent_dictionary = {}
season_dictionary = {}
probability_dictionary = {}
branchesOfSeason = []
BranchPath = []
LeafBranch = []

def process_branch(index, parent, path):
    # Base case: Stop recursion if index is beyond the last level
    if index >= len(branch_split_per_season):
        return

    for _ in range(branch_split_per_season[index]):
        current_branch = branches_of_season[index].pop(0)
        season_dictionary[current_branch] = Season[index]
        parent_dictionary[current_branch] = parent if parent is not None else current_branch
        probability_dictionary[current_branch] = 1.0 / number_of_branches_per_season[index]
        branchesOfSeason.append((Season[index], current_branch))

        updated_path = path +[current_branch]
        # Recursive call for the next level, passing the current branch as the new parent
        process_branch(index + 1, current_branch, updated_path)

        # Handling for leaf branches at the deepest recursive level processed
        if index + 1 == len(branch_split_per_season):
            LeafBranch.append(current_branch)
            BranchPath.append(tuple(updated_path))

process_branch(0, None, [])


parent_dictionary = {key: parent_dictionary[key] for key in sorted(parent_dictionary)}
season_dictionary = {key: season_dictionary[key] for key in sorted(season_dictionary)}
probability_dictionary = {key: probability_dictionary[key] for key in sorted(probability_dictionary)}

#print(parent_dictionary)
#print(season_dictionary)
#print(probability_dictionary)

HoursAndSeasonOfBranch = []
HoursOfBranch = []

for branch in all_branches:
    season = season_dictionary[branch]
    for (s,h) in HoursOfSeason:
        if s == season:
            HoursOfBranch.append((branch,h))
            HoursAndSeasonOfBranch.append((branch,s,h))

if branch_generation:
    tick = time.time()
    generate_random_scenario(filepath = branch_data_path,
                             tab_file_path = tab_file_path,
                             number_of_branches = number_of_branches,
                             parent_dictionary = parent_dictionary,
                             season_dictionary = season_dictionary,
                             regular_seasons = regular_seasons,
                             Periods = NoOfPeriods,
                             weekHours = weekHours,
                             weeksPerMonth = weeksPerMonth,
                             peakSeasonHours = lengthPeakSeason,
                             HoursOfRegSeason=HoursOfRegSeason,
                             HoursOfPeakSeason=HoursOfPeakSeason,
                             dict_countries = dict_countries,
                             representative_countries=representative_countries.values(),
                             representative_countries_h2=representative_countries_H2.values(),
                             fix_sample=FIX_SAMPLE,
                             REDUCED_GEN = REDUCED_GEN
                             )
    tock = time.time()
    print("{hour}:{minute}:{second}: Scenario generation took [sec]:".format(
    hour=datetime.now().strftime("%H"), minute=datetime.now().strftime("%M"), second=datetime.now().strftime("%S")) + str(tock - tick))

include_results = [
                    'results_hydrogen_use',
                    'results_output_transmission',
                    'results_output_gen',
                    'results_output_curtailed_prod',
                    'results_natural_gas_hydrogen',
                    'results_output_gen_el',
                    'results_objective',
                    'results_objective_detailed',
                    'results_objective_transmission',
                    'results_output_stor',
                    'results_hydrogen_storage_investments',
                    'results_hydrogen_production_investments',
                    'results_output_OperationalEL',
                    'results_hydrogen_storage_operational',
                    'results_output_transmission_operational',
                    'time_usage',
                    'results_hydrogen_production',
                    'results_hydrogen_reformer_detailed_investments',
                    'results_output_Operational',
                    'results_output_EuropeSummary',
                    'results_hydrogen_pipeline_investments',
                    'numerics_info',
                    'results_power_balance',
                    'results_hydrogen_pipeline_operational',
                    'results_hydrogen_load_shed',
                    'results_power_storage_operational'
                    ]

reset_investment_files(workbook_path)

for i in range(1,8,2):
    generate_tab_files(filepath = workbook_path, tab_file_path = tab_file_path,
                 hydrogen = True, GREEN_HYDROGEN=GREEN_HYDROGEN, RENEWABLE_GRID_RULE=RENEWABLE_GRID_RULE)
    
    CurrentPeriods = [i,i+1,i+2]
    updatePeriods = [i,i+1]
    if i == 7:
        CurrentPeriods = [7,8]
        updatePeriods = [7,8]

    if CurrentPeriods[-1] == NoOfPeriods:
        last_run = True
    else: 
        last_run = False

    print('------------PERIOD '+str(i)+'------------')

    run_empire(name = name,
            tab_file_path = tab_file_path,
            data_handler_path = data_handler_path,
            result_file_path = result_file_path,
            branch_generation = branch_generation,
            branch_data_path = branch_data_path,
            solver = solver,
            temp_dir = temp_dir,
            FirstHoursOfRegSeason = FirstHoursOfRegSeason,
            lengthRegSeason = lengthRegSeason,
            Period = Period,
            NoOfPeriods = NoOfPeriods,
            CurrentPeriods = CurrentPeriods,
            last_run=last_run,
            updatePeriods = updatePeriods,
            Operationalhour = Operationalhour,
            #Scenario = Scenario,
            Branch = all_branches,
            ParentDictionary = parent_dictionary,
            #SeasonDictionary = season_dictionary,
            ProbabilityDictionary = probability_dictionary,
            HoursAndSeasonOfBranch = HoursAndSeasonOfBranch,
            HoursOfBranch = HoursOfBranch,
            BranchesOfSeason = branchesOfSeason,
            BranchPath = BranchPath,
            Season = Season,
            HoursOfSeason = HoursOfSeason,
            NoOfRegSeason=NoOfRegSeason,
            discountrate = discountrate,
            WACC = WACC,
            LeapYearsInvestment = LeapYearsInvestment,
            WRITE_LP = WRITE_LP,
            PICKLE_INSTANCE = PICKLE_INSTANCE,
            EMISSION_CAP = EMISSION_CAP,
            USE_TEMP_DIR = USE_TEMP_DIR,
            SEASONAL_STORAGE = SEASONAL_STORAGE,
            FLEX_HYDROGEN = FLEX_HYDROGEN,
            HYDROGEN_CONSTANT_DEMAND = HYDROGEN_CONSTANT_DEMAND,
            REFORMER_HYDROGEN=REFORMER_HYDROGEN,
            GREEN_HYDROGEN=GREEN_HYDROGEN,
            include_results = include_results,
            MaxChargeAndDischargePercentage = MaxChargeAndDischargePercentage,
            RENEWABLE_GRID_RULE = RENEWABLE_GRID_RULE,
            start_year=2021,
            H2LoadScale=H2LoadScale
            )
    gc.collect()