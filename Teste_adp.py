import configparser
import os
from pcraster.framework import dynamicBase
from pcraster.framework import *
import pcraster as pcr



# Nome do arquivo de configuraçoes
configFile = 'config.ini'

# Leitura de arquivo config.ini
config = configparser.ConfigParser()
config.read(configFile)
# Leitura de local de arquivos de entrada
files = config.get('FILES', 'dir')
dem_file = config.get('FILES', 'dem')

# Alterar local de rodada do algoritmo para pasta indicada no config
os.chdir(files)

# Set clone
setclone(dem_file)
Dem = readmap(dem_file)
ldd1 = lddcreate(Dem, 1e31, 1e31, 1e31, 1e31)
report(ldd1, "ldd.map")
print("Finalizado")



