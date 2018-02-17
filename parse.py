import struct

p01 = struct.Struct('2s14s150s')
t01_columns = ['cnpj', 'nome_empresarial']

def parse_t01(line):

	dados = [s.decode('iso-8859-1').strip() for s in p01.unpack(line[:166].encode('iso-8859-1'))]

	return dict(zip(t01_columns, dados[1:]))

p02 = struct.Struct('2s14s1s14s2s150s')
t02_columns = ['cnpj', 'tipo_pessoa', 'cpf_cnpj', 'qualificacao_socio', 'nome_socio']

def parse_t02(line):

	dados = [s.decode('iso-8859-1').strip() for s in p02.unpack(line[:183].encode('iso-8859-1'))]

	return dict(zip(t02_columns, dados[1:]))


import sys
import logging
import pandas as pd
import codecs

if __name__ == '__main__':

	log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(level=logging.INFO, format=log_fmt)
	logger = logging.getLogger("RemuneracaoFederalExtractor")

	filename = sys.argv[1]

	empresas = []
	socios = []

	with codecs.open(filename, 'r', 'iso-8859-15') as lines:

		id_empresa_atual = 0

		for n, line in enumerate(lines):
			
			logger.info('Reading line: {} size: {} inicio: {}'.format(n, len(line), line[:10]))
			
			tipo = line[:2]
			if tipo == '01':
				empresa = parse_t01(line)
				empresa['id'] = id_empresa_atual
				empresas.append(empresa)
				id_empresa_atual += 1
			elif tipo == '02':
				socio = parse_t02(line)
				socio['id_empresa'] = id_empresa_atual
				socios.append(socio)
			else:
				raise Exception('Valor de tipo errado. Valor: {}\nLinha: {}'.format(tipo, line))
	
	empresas_df = pd.DataFrame(empresas)
	empresas_df.to_csv("empresas.csv")

	socios_df = pd.DataFrame(socios)
	socios_df.to_csv("socios.csv")
	
