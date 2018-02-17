import struct
import sys
import logging
import codecs
import csv

ENCODING = 'iso-8859-15'

p01 = struct.Struct('2s14s150s')
t01_columns = ['cnpj', 'nome_empresarial']


def parse_t01(l):
    dados = [s.decode(ENCODING).strip() for s in p01.unpack(l[:166].encode(ENCODING))]

    return dict(zip(t01_columns, dados[1:]))


p02 = struct.Struct('2s14s1s14s2s150s')
t02_columns = ['cnpj', 'tipo_pessoa', 'cpf_cnpj', 'qualificacao_socio', 'nome_socio']


def parse_t02(l):
    dados = [s.decode(ENCODING).strip() for s in p02.unpack(l[:183].encode(ENCODING))]

    return dict(zip(t02_columns, dados[1:]))


if __name__ == '__main__':

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger("CNPJs")

    input_filename = sys.argv[1]
    state = sys.argv[2]

    with codecs.open(input_filename, 'r', ENCODING) as f, \
            open('socios_{}.csv'.format(state), 'w') as f_socios, \
            open('empresas_{}.csv'.format(state), 'w') as f_empresas:

        writer_socios = csv.DictWriter(f_socios, fieldnames=t02_columns + ['id_empresa'])
        writer_socios.writeheader()
        writer_empresas = csv.DictWriter(f_empresas, fieldnames=t01_columns + ['id'])
        writer_empresas.writeheader()

        id_empresa_atual = 0

        for n, line in enumerate(f):

            logger.info('Reading line: {} size: {} inicio: {}'.format(n, len(line), line[:10]))

            tipo = line[:2]
            if tipo == '01':
                empresa = parse_t01(line)
                id_empresa_atual += 1
                empresa['id'] = id_empresa_atual
                writer_empresas.writerow(empresa)

            elif tipo == '02':
                socio = parse_t02(line)
                socio['id_empresa'] = id_empresa_atual
                writer_socios.writerow(socio)
