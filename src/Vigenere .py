import collections

#Variáveis globais
coincidence_index_pt = 0.072723
alphabet = map(chr, range(65, 91)) #dict.fromkeys(map(chr, range(65, 91)), 0)
max_key_size = 26

#Encontrar o tamanho da chave
def find_key_size(ciphered_text):
    for i in range(len(ciphered_text)):
        print(ciphered_text[i:], '\n')

def get_coincidence_index_from(text):

    #Normaliza o texto
    text = text.replace(' ', '').upper()
    text_size = len(text)

    #Contabiliza a ocorrência de cada caractere
    frequences = collections.Counter(text)

    #Calcula o índice de coincidência
    return sum(frequences[char] * (frequences[char] - 1) for char in alphabet) / (text_size * (text_size-1))

IC = "%.3f" % get_coincidence_index_from('SOTHATCIPHERTEXTLOOKSLIKETHIS')
print(IC)


#print("%.3f" % IC, "({})".format(IC))