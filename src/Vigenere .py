import collections
import math
import string

#https://docs.python.org/2/library/collections.html
#https://en.wikipedia.org/wiki/Index_of_coincidence
#https://pages.mtu.edu/~shene/NSF-4/Tutorial/VIG/Vig-IOC.html
#https://www.nku.edu/~christensen/1402%20Friedman%20test%202.pdf
#http://numaboa.com.br/criptografia/criptoanalise/310-frequencia-portugues
#http://practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-vigenere-cipher/

portuguese = {
    'A':0.1463,
    'B':0.0104,
    'C':0.0388,
    'D':0.0499,
    'E':0.1257,
    'F':0.0102,
    'G':0.013,
    'H':0.0078,
    'I':0.0618,
    'J':0.039,
    'K':0.001,
    'L':0.0277,
    'M':0.0473,
    'N':0.0444,
    'O':0.0973,  
    'P':0.0252,
    'Q':0.012,
    'R':0.0653,
    'S':0.068,
    'T':0.0433,
    'U':0.0363,
    'V':0.0157,
    'W':0.0003,
    'X':0.0025,
    'Y':0.0006,
    'Z':0.0047
}

english = {
    'A':0.0816,
    'B':0.0149,
    'C':0.0278,
    'D':0.0425,
    'E':0.1270,
    'F':0.0222,
    'G':0.0201,
    'H':0.0609,
    'I':0.0696,
    'J':0.0015,
    'K':0.0077,
    'L':0.0402,
    'M':0.024,
    'N':0.0674,
    'O':0.075,
    'P':0.0192,
    'Q':0.009,
    'R':0.0598,
    'S':0.0632,
    'T':0.0905,
    'U':0.0275,
    'V':0.0097,
    'W':0.0236,
    'X':0.015,
    'Y':0.0197,
    'Z':0.007
}

#Variáveis globais
coincidence_index_pt = 0.072723
#coincidence_index_en = 0.0686
max_key_size = 26

#Implementa a fórmula do índice de coincidência
def get_coincidence_index_from(text):
    text_size = len(text)

    #Contabiliza a ocorrência de cada caractere (frequência)
    frequences = collections.Counter(text)
    
    #Calcula o índice de coincidência e define o resultado para três casas decimais após a vírgula
    return float( '%.6f' % (sum(freq * (freq-1) for freq in frequences.values()) / (text_size * (text_size-1))))

#Esta função gera as substrings do texto e calcula o índice de coincidência
def get_ioc_table_from(text):

    #Normaliza o texto (Remove espaços / deixa o texto em uppercase)
    text = text.replace(' ', '').lower()

    #Representa um iterável(1 - 26) com todos os tamanhos de chaves possívels
    probable_keys = range(max_key_size)
    
    #Dicionário para armazenar os candidatos de tamanhos de chave
    #Cada candidato mapeia para um conjunto de índices de coincidência
    coincidence_index_list = {}

    # i É o tamanho chave
    for i in probable_keys:
        for j in range(i):

            # Cria uma substring, pulando o i-ésimo caractere
            substring = ''.join(text[j::i])

            # Cadeias muito pequenas não são tão relevantes na busca, então pulamos
            if len(substring) < 3:
                continue
            
            # Índice de coincidência neutro é indiferente no cálculo, então pulamos também
            ioc = get_coincidence_index_from(substring)
            if ioc == 0.0:
                continue

            if i not in coincidence_index_list:
                coincidence_index_list[i] = {ioc}
                continue

            coincidence_index_list[i].add(ioc)

    return coincidence_index_list

def find_key_size(text, k):

    password = ''

    for i in range(k):

        # Monta a string com os n-ésimos caracteres
        substring = text[i::k]

        #Aplica a análise de frequência
        frequency = collections.Counter(substring)

        #Obtém o caractere de maior frequência
        scores = sorted(frequency.items(), reverse = True, key=lambda item: item[1])

        #print(scores)
        #Obtém o caractere da chave na i-ésima posição
        first_offset = string.ascii_lowercase.index(scores[0][0])
        second_offset = string.ascii_lowercase.index(scores[1][0])

        password += string.ascii_lowercase[min(first_offset, second_offset)]

        if len(password) >= key:
            break

        #0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
        #A B C D E F G H I J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
    
    return password

f = open("cipher7.txt", "r").read()

print('attempt to build the index of coincidence table from stream...')
result = get_ioc_table_from(f)

print('attempt to get the password... ', end='')

# Cuidar o tamanho da chave que às vezes vem errado
key,_ = min(result.items(), key = lambda kv : abs(sum(kv[1]) / len(kv[1]) - coincidence_index_pt))

print('key is probably', key)

print('attempt to get the plain text password... ', end='')
pw = find_key_size(f, key)

print('figured:', pw)