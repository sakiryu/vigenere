import collections
import math
import string
import os
import sys

#Referências

# https://pt.wikipedia.org/wiki/Qui-quadrado
# https://pages.mtu.edu/~shene/NSF-4/Tutorial/VIG/Vig-Recover.html
# https://pages.mtu.edu/~shene/NSF-4/Tutorial/VIG/Vig-IOC.html
# http://numaboa.com.br/criptografia/criptoanalise/310-frequencia-portugues

# Variáveis globais (python não tem const, então simplesmente não mudamos as variáveis)
COINCIDENCE_INDEX_PT = 0.072723
MOST_COMMON_CHAR_OVERALL = ord('a')
PT_FREQUENCY_TABLE = {
    'a':0.1463,
    'b':0.0104,
    'c':0.0388,
    'd':0.0499,
    'e':0.1257,              
    'f':0.0102,
    'g':0.013,
    'h':0.0078,
    'i':0.0618,
    'j':0.039,
    'k':0.001,
    'l':0.0277,
    'm':0.0473,
    'n':0.0444,
    'o':0.0973,    
    'p':0.0252,
    'q':0.012,
    'r':0.0653,
    's':0.068,
    't':0.0433,    
    'u':0.0363,
    'v':0.0157,
    'w':0.0003,
    'x':0.0025,
    'y':0.0006,
    'z':0.0047
}

# Conta a frequência de cada letra no texto passado como argumento
# e aplica a fórmula do índice de coincidência
def get_coincidence_index_from(text):
    text_size = len(text)

    # Contabiliza a ocorrência de cada caractere
    frequences = collections.Counter(text)
    
    # Calcula o índice de coincidência
    return float(sum(freq * (freq-1) for freq in frequences.values()) / (text_size * (text_size-1)))

# Esta função gera as substrings do texto
# Calcula o índice de coincidência para cada string gerada
# No fim, soma todos os idc e faz a média para cada possível chave
def get_ioc_table_from(ciphered_text):

    max_key_size = len(PT_FREQUENCY_TABLE)
    probable_keys = range(max_key_size)
    
    # Dicionário para armazenar os candidatos de tamanhos de chave
    # Cada candidato mapeia para um conjunto de índices de coincidência
    coincidence_index_list = {}

    # i É o tamanho chave
    for i in probable_keys:
        for j in range(i):

            # Cria uma substring, pulando o i-ésimo caractere
            substring = ''.join(ciphered_text[j::i])

            # Cadeias muito pequenas não são tão relevantes na busca, então pulamos
            if len(substring) < 3:
                continue
            
            # Índice de coincidência neutro é indiferente no cálculo, então pulamos também
            ioc = get_coincidence_index_from(substring)
            if ioc == 0.0:
                continue

            if i not in coincidence_index_list:
                coincidence_index_list[i] = [ioc]
                continue

            coincidence_index_list[i].append(ioc)

    # Faz a média de cada conjunto de índices
    for ioc in coincidence_index_list:
        coincidence_index_list[ioc] = float(sum(coincidence_index_list[ioc]) / len(coincidence_index_list[ioc]))

    return coincidence_index_list

# Essa função recebe o texto cifrado e o tramanho da chave
# monta n colunas (n = tamanho da chave), contabiliza as ocorrências de letras
# seleciona as duas mais frequêntes e as compara na tabela de frequência da língua portuguesa.
# se a letra mais recorrente no texto cifrado tiver uma frequência inferior ao da segunda letra
def get_plaintext_password(ciphered_text, k):

    password = str()

    for i in range(k):
        # Monta a substring de i até k, pulando de k em k
        substring = ciphered_text[i::k]

        # Contabiliza a ocorrência de cara caractere e pega os dois mais comuns
        occurrences = collections.Counter(substring).most_common(2)

        first_most_freq_char = occurrences[0][0]
        second_most_freq_char = occurrences[1][0]
        
        # Observar a tabela de frequência da língua portuguesa e verificar se a segunda 
        # letra mais recorrente no texto possui uma frequência maior do que a primeira.
        # Aplica o teste do X^2 caso a condição não seja satisfeita.
        password += second_most_freq_char if PT_FREQUENCY_TABLE[first_most_freq_char] < PT_FREQUENCY_TABLE[second_most_freq_char] else get_letter_from_frequency(substring)
    return password

# Retorna a letra mais provável de ser da chave através da análise de frequência sobre um bloco de texto cifrado
# A análise é feita com o método Qui-Quadrado(X^2) para descobrir a similaridade de duas distribuições de probabilidade (neste caso, o texto cifrado e a distribuição de letras da lingua portuguesa).  
def get_letter_from_frequency(ciphered_block):

    chi_squareds = {}
    block_size = len(ciphered_block)

    for i in range(26):
        chi_squared_sum = 0.0

        offset = [chr(MOST_COMMON_CHAR_OVERALL + ((ord(letter) - MOST_COMMON_CHAR_OVERALL - i) % 26)) for letter in ciphered_block]
        occurrences = collections.Counter(offset)

        #Calcula o percentual de frequência e compara com as frequências da lingua portuguesa
        for oc in occurrences:
            occurrences[oc] *= (1.0 / float(block_size))
            chi_squared_sum += ((occurrences[oc] - math.pow(PT_FREQUENCY_TABLE[oc], 2)) / PT_FREQUENCY_TABLE[oc])
        
        chi_squareds[i] = chi_squared_sum

    # A menor diferença entre a distribuição do texto cifrado e da lingua portuguesa 
    # indica que as frequências são próximas, implicando no melhor candidato para ser 
    # a letra da chave que precisa ser deslocada
    return chr(min(chi_squareds, key = chi_squareds.get) + MOST_COMMON_CHAR_OVERALL)

# Realiza a etapa de subtração entre a letra do texto cifrado
# e a letra da chave, para obter a posição do alfabeto correspondente
# a letra não cifrada
def decrypt(ciphered_text, plainKey):

    k = len(plainKey)
    deciphered_text = str()
    for i, c in enumerate(ciphered_text):

        # Rotaciona a chave para todos as letras do texto cifrado
        # Faz a diferença entre elas para descobrir a posição da letra
        # não cifrada
        difference = ord(c) - ord(plainKey[i % k])
        deciphered_text += string.ascii_lowercase[difference % 26]

    return deciphered_text


if __name__ == "__main__":

    args = sys.argv[1:]
    if(len(args) < 1):
        print('Usage: Vegenere.py <ciphered_file>')

    file_name = args[0]

    ciphered_file = open(file_name, "r").read()

    print('Analyzing {}...'.format(file_name))
    ioc_table = get_ioc_table_from(ciphered_file)

    print('Guessing the key length... ', end = '')
    key,_ = min(ioc_table.items(), key = lambda i : abs(float('%.3f' % i[1]) - COINCIDENCE_INDEX_PT))
    print(key)

    print('Attempt to recover the password... ', end = '')
    pw = get_plaintext_password(ciphered_file, key)
    print(pw)

    print('Recovering file... ', end = '')
    deciphered_text = decrypt(ciphered_file, pw)

    if not os.path.exists('results'):
        os.mkdir('results')

    deciphered_file = open('results/{}'.format(file_name), 'w')
    deciphered_file.write(deciphered_text)
    deciphered_file.close()

    print('Done.')
    print('Deciphered file is stored in results/ folder.')