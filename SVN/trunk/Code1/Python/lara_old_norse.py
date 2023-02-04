
import lara_utils

edda_words2lemmas_file = '$LARA/Code/LinguisticData/oldnorse/edda_words2lemmas.json'
#onp_index_file = '$LARA/Code/LinguisticData/oldnorse/corpus/onp_index.json'
onp_index_file = '$LARA/Code/LinguisticData/oldnorse/onp_index_extended.json'
EddaWordsAndLemmasDict = lara_utils.read_json_file(edda_words2lemmas_file)
ONPDict = lara_utils.read_json_file(onp_index_file)

# Use above resources to try to get POS information for an Old Norse word from the Edda
def old_norse_word_to_pos(Word):
    if Word not in EddaWordsAndLemmasDict:
        return 'None'
    Lemma = EddaWordsAndLemmasDict[Word][0]
    return old_norse_lemma_to_pos(Lemma)

def old_norse_lemma_to_pos(Lemma):
    if Lemma not in ONPDict:
        return 'None'
    ONPInfo = ONPDict[Lemma]
    return ONPInfo[0]['pos'] if 'pos' in ONPInfo[0] else 'None'

def reduced_form_of_old_norse_pos(POS):
    Components = POS.split()
    return Components[0] if len(Components) != 0 else 'None'
