from openalpr import Alpr
import sys

alpr = Alpr("br", "openalpr.conf", "runtime_data")

if not alpr.is_loaded():
    print("Erro ao carregar OpenALPR")
    sys.exit(1)

alpr.set_top_n(20)
alpr.set_default_region("br") 

results = alpr.recognize_file("img.jpg")

print(results)
