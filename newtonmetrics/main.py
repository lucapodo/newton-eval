from vegazero.VegaZero2VegaLite import VegaZero2VegaLite
import pandas as pd
import altair as alt
from draco import Draco
from draco.schema import schema_from_dataframe
import pandas as pd
from termcolor import colored
from draco.fact_utils import dict_to_facts, answer_set_to_dict
from draco.run import run_clingo
from newton.newton import Newton
import os 
os.system('clear')

vegazero = "mark area data payments encoding x payment_type_code y aggregate average amount_paid group x"
ground = "mark line data payments encoding x payment_type_code y aggregate average amount_paid group x"

vz = VegaZero2VegaLite()
d = Draco()
df = pd.read_csv('./payments.csv')

isCompling = False

try:
    # vegalite_gen, _ = vz.to_VegaLite(vegazero, df)
    vegalite_gen_, vegazero_spec_ = vz.to_VegaLite(vegazero)
    vegalite_gen_ground_, vegazero_ground_spec_ = vz.to_VegaLite(ground)

    print(colored(vegalite_gen_, 'blue'))
    print(colored('VegaZero correctly compiled', 'green'))

    isCompling = True

    print(colored(f'How much is the generated equals to the groundtruth? Score: {vz.vega_zero_groundtruth_similarity_score(vegazero, ground)}', 'green')) #bonus
    print(colored(f'Did it missed the query explicitness? Score: {vz.expliciteness_missed_score("area", vegazero)}', 'green')) # piu accuracy che explicitness
    #sotto controlli: marker, dati 

except Exception as e:
    print(colored(f'error vegalite compile : {e}', 'red'))

if (isCompling):
    
    schema: dict = schema_from_dataframe(df) #Generating the data schema to extract the field types automatically
    spec = dict_to_facts(schema | vegalite_gen_) #converte in fact e concatena data e vis

    isVisCorrect = d.check_spec(spec)
    print(colored(f"Does it respects all the hard contraints ? {isVisCorrect}", 'green'))
    print(colored(f"Number of soft violations: {len(d.get_violations(spec))}", 'blue'))

    isMarkCorrect = vegazero_spec_['mark'] == vegazero_ground_spec_['mark']
    print(colored(f"Does it pick the right marker? {isMarkCorrect}", 'green' if isMarkCorrect else 'red'))

    isXCorrect = vegazero_spec_['encoding']['x'] == vegazero_ground_spec_['encoding']['x']
    print(colored(f"Does it pick the right x? {isXCorrect}", 'green' if isXCorrect else 'red'))

    isYCorrect = vegazero_spec_['encoding']['y']['y'] == vegazero_ground_spec_['encoding']['y']['y']
    print(colored(f"Does it pick the right y? {isYCorrect}", 'green' if isYCorrect else 'red'))

    


