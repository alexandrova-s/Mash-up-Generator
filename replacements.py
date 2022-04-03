from similarities import find_similarities, get_indexes_of_minima 

''' script with functions making parts exchanges based on fragments durations 
    splitted based on silence moments in songs '''

def replace_vocals(voc1, voc2, full_vocal1, full_vocal2, accompaniment):
    list_of_minima = []
    all_similarities = list(find_similarities(voc1, voc2))
    for x in all_similarities:
        list_of_minima.append(x[1][1])
    sorted_indexes = get_indexes_of_minima(list_of_minima)
    for index_of_minimum in sorted_indexes:
        to_replace = all_similarities[index_of_minimum]
        try:
            next_to_replace = all_similarities[index_of_minimum+1]
        except:
            pass
        print(f"Change in: {to_replace[0].start}")
        vocal_replacement = full_vocal2[to_replace[1][0].start:to_replace[1][0].stop]
        accompaniment = accompaniment.overlay(vocal_replacement, position=to_replace[0].start)
        next_replacement = full_vocal1[to_replace[1][0].stop:next_to_replace[1][0].start]
        accompaniment = accompaniment.overlay(next_replacement, position=to_replace[0].stop)
    return accompaniment

def replace_vocals_accompaniament(voc1, voc2, full_vocal1, full_vocal2, accompaniament): #, number_of_fragments_to_replace):
    list_of_minima = []
    all_similarities = list(find_similarities(voc1, voc2))
    for x in all_similarities:
        list_of_minima.append(x[1][1])
    print('Minima', list_of_minima)
    # index_of_minimum = list_of_minima.index(min(list_of_minima))
    sorted_indexes = get_indexes_of_minima(list_of_minima)
    for index_of_minimum in sorted_indexes[:len(list_of_minima)-1]:
        to_replace = all_similarities[index_of_minimum]
        print(to_replace)
        print(f"Change in: {to_replace[0][0]}")
        vocal_replacement = full_vocal2[to_replace[1][0][0]:to_replace[1][0][1]]
        accompaniament = accompaniament.overlay(vocal_replacement, position=to_replace[0][0])
    return accompaniament
