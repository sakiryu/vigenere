import collections
import math
import string
import os

#Referências
#https://docs.python.org/2/library/collections.html
#https://en.wikipedia.org/wiki/Index_of_coincidence
#https://pages.mtu.edu/~shene/NSF-4/Tutorial/VIG/Vig-IOC.html
#https://www.nku.edu/~christensen/1402%20Friedman%20test%202.pdf
#http://numaboa.com.br/criptografia/criptoanalise/310-frequencia-portugues
#http://practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-vigenere-cipher/

#Variáveis globais (python não tem const, então simplesmente não mudamos as variáveis)
coincidence_index_pt = 0.072723
max_key_size = 26

#Conta a frequência de cada letra no texto passado como argumento
#e aplica a fórmula do índice de coincidência
def get_coincidence_index_from(text):
    text_size = len(text)

    #Contabiliza a ocorrência de cada caractere (frequência)
    frequences = collections.Counter(text)
    
    #Calcula o índice de coincidência e define o resultado para três casas decimais após a vírgula
    return float(sum(freq * (freq-1) for freq in frequences.values()) / (text_size * (text_size-1)))

#Esta função gera as substrings do texto
#Calcula o índice de coincidência para cada string gerada
#No fim, soma todos os idc e faz a média para cada possível chave
def get_ioc_table_from(ciphered_text):

    probable_keys = range(max_key_size)
    
    #Dicionário para armazenar os candidatos de tamanhos de chave
    #Cada candidato mapeia para um conjunto de índices de coincidência
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

    for ioc in coincidence_index_list:
        coincidence_index_list[ioc] = float((sum(coincidence_index_list[ioc]) / len(coincidence_index_list[ioc])))

    return coincidence_index_list

def get_plaintext_password(ciphered_text, k):

    password = str()

    for i in range(k):

        # Monta a string com os n-ésimos caracteres
        substring = ciphered_text[i::k]

        #Aplica a análise de frequência
        frequency = collections.Counter(substring)

        #Obtém o caractere de maior frequência
        scores = sorted(frequency.items(), reverse = True, key = lambda item: item[1])
        password += scores[1][0]

        if len(password) >= k:
            break

    return password

#Realiza a etapa de subtração entre a letra do texto cifrado
#e a letra da chave, para obter a posição do alfabeto correspondente
#a letra não cifrada
def decrypt(ciphered_text, plainKey):

    k = len(plainKey)
    deciphered_text = str()
    for i, c in enumerate(ciphered_text):
        difference = ord(c) - ord(plainKey[i % k])
        
        if difference < 0:
            difference += 26

        deciphered_text += string.ascii_lowercase[difference]

    return deciphered_text

# A B C D E F G H I J K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25

def main():
    if not os.path.exists('results'):
        os.mkdir('results') 

    for i in range(1, 32):

        fName = "cipher{}.txt".format(i)

        print('analyzing', fName)
        ciphered_file = open(fName, "r").read()
        
        #Normaliza o texto (Remove espaços / deixa o texto em uppercase)
        ciphered_file = ciphered_file.replace(' ', '').lower()

        ioc_table = get_ioc_table_from(ciphered_file)

        print('attempt to get the password... ', end='')

        key,_ = min(ioc_table.items(), key = lambda i : abs(float('%.3f' % i[1]) - coincidence_index_pt))
        print('key size:', key)

        print('attempt to get the plain text password... ', end='')
        pw = get_plaintext_password(ciphered_file, key)
        print('pw:', pw)

        deciphered_text = decrypt(ciphered_file, pw)

        deciphered_file = open('results/de{}'.format(fName), 'w')
        deciphered_file.write(deciphered_text)
        deciphered_file.close()