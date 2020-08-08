#!/usr/bin/python3

import argparse
import os
import signal
import sys
import time
import unicodedata

import pandas as pd


################################################
# utilities
################################################


def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def signal_handler(signal, frame):
    print("\nCTRL-C detected. Exiting...")
    sys.exit(0)


################################################
# data processing
################################################

def process_input(filename):
    time_start = time.time()
    print('Processing input file...')
    input_file = open(filename, "r", encoding="utf8")
    content = input_file.read()
    input_file.close()
    print('Removing accents...')
    processed_data = \
        unicodedata.normalize('NFKD', content) \
            .encode('ascii', 'ignore') \
            .decode('utf8') \
            .upper()
    time_end = time.time()
    print('Finished in %.2fs.\n' % (time_end - time_start))
    return processed_data


def normalize_data(csv_file):
    print('Loading entries...')
    data = pd.read_csv(csv_file,
                       engine='python',
                       verbose=False,
                       encoding='utf-8',
                       delimiter=';',
                       memory_map=True)
    print('Loaded %i entries' % len(data.index))

    print('Normalizing data...')
    time_start = time.time()

    data.fillna('N/A', inplace=True)
    data.rename(
        columns={
            'DATA DA NOTIFICACAO': 'DT_NOTIFIC',
            'DATA DE NASCIMENTO': 'DAT_NASC',
            'DATA DE COLETA DO TESTE': 'DT_COLETA',
            'DATA DO INICIO DOS SINTOMAS': 'DT_SIN_PRI',
            'BAIRRO': 'NM_BAIRRO',
            'MUNICIPIO DE RESIDENCIA': 'MUN_RES',
            'NOME COMPLETO': 'NM_PACIENT',
            'NUMERO DA NOTIFICACAO': 'NU_NOTIFIC',
            'RESULTADO DO TESTE': 'RESULTADO',
            'SINTOMA- DISPNEIA': 'DISPNEIA',
            'SINTOMA- DOR DE GARGANTA': 'GARGANTA',
            'SINTOMA- FEBRE': 'FEBRE',
            'SINTOMA- TOSSE': 'TOSSE',
            'SINTOMA- OUTROS': 'OUT_SINT',
            'TIPO DE TESTE': 'REQUI_GAL'
        },
        inplace=True)
    data['SEXO'] = data['SEXO'].replace('MASCULINO', 'M').replace('FEMININO', 'F')

    time_end = time.time()
    print('Finished in %.2fs.\n' % (time_end - time_start))
    return data


def export_excel(output_file, data):
    print('Exporting excel file...')
    time_start = time.time()
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    data.to_excel(writer, 'COVID')
    writer.save()
    time_end = time.time()
    print('Export finished in %.2fs\n' % int(time_end - time_start))


################################################
# main
################################################


def main(args):
    clear()
    print('\n===============\n= eSUS Parser =\n===============\n')

    # parse arguments
    description_txt = 'Um parser para dados do sistema e-SUS VE ( https://notifica.saude.gov.br )'
    parser = argparse.ArgumentParser(description=description_txt)
    parser.add_argument("input_file", help='input csv file', type=str)

    # read arguments from CLI
    args = parser.parse_args()
    input_file = args.input_file

    data = process_input(input_file)

    print('Saving temporary file...\n')
    name, ext = os.path.splitext(input_file)
    temp_filename = "{name}{ext}.temp".format(name=name, ext=ext)
    temp_file = open(temp_filename, 'w', encoding='utf8')
    temp_file.write(data)
    temp_file.close()

    print('Generating spreadsheet...')
    spreadsheet = normalize_data(temp_filename)

    output_file = "{name}_normalized.xlsx".format(name=name)
    export_excel(output_file, spreadsheet)

    print('Removing temporary file...')
    os.remove(temp_filename)

    print('Done.')


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
