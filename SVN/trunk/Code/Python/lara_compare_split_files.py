
import lara_utils
import difflib

def print_diffs_le_chien_jaune():
    print_split_files_diff_summary('Le chien jaune',
                                   '$LARA/Content/le_chien_jaune/generated_files/le_chien_jaune_split_initial.json',
                                   '$LARA/Content/le_chien_jaune/generated_files/le_chien_jaune_split_8hours.json',
                                   '$LARA/Content/le_chien_jaune/generated_files/le_chien_jaune_surface_diff.txt',
                                   '$LARA/Content/le_chien_jaune/generated_files/le_chien_jaune_lemma_diff.txt',
                                   '$LARA/Content/le_chien_jaune/generated_files/le_chien_jaune_surface_and_lemma_diff.txt')

def print_diffs_animal_farm():
    print_split_files_diff_summary('Animal Farm',
                                   '$LARA/Content/animal_farm/generated_files/animal_farm_split_initial.json',
                                   '$LARA/Content/animal_farm/generated_files/animal_farm_split_6hours.json',
                                   '$LARA/Content/animal_farm/generated_files/animal_farm_surface_diff.txt',
                                   '$LARA/Content/animal_farm/generated_files/animal_farm_lemma_diff.txt',
                                   '$LARA/Content/animal_farm/generated_files/animal_farm_surface_and_lemma_diff.txt')

def print_diffs_kallocain():
    print_split_files_diff_summary('Kallocaine',
                                   '$LARA/Content/kallocain/generated_files/kallocain_split_initial.json',
                                   '$LARA/Content/kallocain/generated_files/kallocain_split_24hours.json',
                                   '$LARA/Content/kallocain/generated_files/kallocain_surface_diff.txt',
                                   '$LARA/Content/kallocain/generated_files/kallocain_lemma_diff.txt',
                                   '$LARA/Content/kallocain/generated_files/kallocain_surface_and_lemma_diff.txt')

def print_diffs_nasrettin_large():
    print_split_files_diff_summary('Kallocaine',
                                   '$LARA/Content/nasrettin_large/generated_files/nasrettin_large_split_v1.json',
                                   '$LARA/Content/nasrettin_large/generated_files/nasrettin_large_split_v2.json',
                                   '$LARA/Content/nasrettin_large/generated_files/nasrettin_surface_diff.txt',
                                   '$LARA/Content/nasrettin_large/generated_files/nasrettin_lemma_diff.txt',
                                   '$LARA/Content/nasrettin_large/generated_files/nasrettin_surface_and_lemma_diff.txt')

def print_diffs_candide():
    print_split_files_diff_summary('Candide',
                                   '$LARA/tmp_resources/candide_from_epub_split.json',
                                   '$LARA/tmp_resources/candide_split.json',
                                   '$LARA/Content/candide/generated_files/candide_surface_diff.txt',
                                   '$LARA/Content/candide/generated_files/candide_lemma_diff.txt',
                                   '$LARA/Content/candide/generated_files/candide_surface_and_lemma_diff.txt')

def print_split_files_diff_summary(Label, File1, File2, SurfaceDiffFile, LemmaDiffFile, SurfaceAndLemmaDiffFile):
    lara_utils.print_and_flush(f'\n--------------------------------')
    lara_utils.print_and_flush(f'Comparing split files: "{Label}"')
    lara_utils.print_and_flush(f'File 1: {File1}')
    lara_utils.print_and_flush(f'File 2: {File2}')
    SurfaceChanged = split_files_diff(File1, File2, 'surface', SurfaceDiffFile)
    LemmaChanged = split_files_diff(File1, File2, 'lemma', LemmaDiffFile)
    split_files_diff(File1, File2, 'surface_and_lemma', SurfaceAndLemmaDiffFile)
    lara_utils.print_and_flush(f'Surface words changed: {SurfaceChanged}')
    lara_utils.print_and_flush(f'Lemmas changed:        {LemmaChanged}')

def split_files_diff(File1, File2, Type, DiffFile):
    Seq1 = split_file_to_sequence(File1, Type)
    Seq2 = split_file_to_sequence(File2, Type)
    d = difflib.Differ()
    lara_utils.print_and_flush(f'--- Performing diff ({Type})...')
    Diff = d.compare(Seq1, Seq2)
    lara_utils.print_and_flush(f'... done')
    DiffLines = [ Line for Line in list(Diff) if Line[0] in '+-' ]
    lara_utils.print_and_flush(f'--- {len(DiffLines)} lines in diff')
    lara_utils.write_lara_text_file('\n'.join(DiffLines), DiffFile)
    return len( [ Line for Line in DiffLines if Line[0] in '-' ] )

def split_file_to_sequence(File, Type):
    Content = lara_utils.read_json_file(File)
    Seq = [ item_to_line(Item, Type) for Page in Content for Segment in Page[1] for Item in Segment[2]
            if Item[1] != '' ]
    lara_utils.print_and_flush(f'--- Found {len(Seq)} items in {File}')
    return Seq

def item_to_line(Item, Type):
    if Type == 'surface':
        return Item[0]
    elif Type == 'lemma':
        return Item[1]
    elif Type == 'surface_and_lemma':
        return f'{Item[0]}|{Item[1]}'

#--------------------------------

##def test(Id):
##    if Id == 'kallocain_small_lemma':
##        compare_split_files('$LARA/Content/kallocain_small/generated_files/kallocain_small_split_initial.json',
##                            '$LARA/Content/kallocain_small/generated_files/kallocain_small_split_edited.json',
##                            'lemma',
##                            '$LARA/Content/kallocain_small/generated_files/kallocain_small_diff.json')
##    if Id == 'kallocain_small_surface_and_lemma':
##        compare_split_files('$LARA/Content/kallocain_small/generated_files/kallocain_small_split_initial.json',
##                            '$LARA/Content/kallocain_small/generated_files/kallocain_small_split_edited.json',
##                            'surface_and_lemma',
##                            '$LARA/Content/kallocain_small/generated_files/kallocain_small_diff.json')
##    elif Id == 'animal_farm_surface':
##        compare_split_files('$LARA/Content/animal_farm/generated_files/animal_farm_20mins_split.json',
##                            '$LARA/Content/animal_farm/generated_files/animal_farm_split.json',
##                            'surface',
##                            '$LARA/Content/animal_farm/generated_files/diff_surface.json')
##    elif Id == 'animal_farm_lemma':
##        compare_split_files('$LARA/Content/animal_farm/generated_files/animal_farm_20mins_split.json',
##                            '$LARA/Content/animal_farm/generated_files/animal_farm_split.json',
##                            'lemma',
##                            '$LARA/Content/animal_farm/generated_files/diff_lemma.json')
##    elif Id == 'animal_farm_surface_and_lemma':
##        compare_split_files('$LARA/Content/animal_farm/generated_files/animal_farm_20mins_split.json',
##                            '$LARA/Content/animal_farm/generated_files/animal_farm_split.json',
##                            'surface_and_lemma',
##                            '$LARA/Content/animal_farm/generated_files/diff_surface_and_lemma.json')
##
##def compare_split_files(File1, File2, Type, OutFile):
##    Seq1 = split_file_to_sequence(File1, Type)
##    Seq2 = split_file_to_sequence(File2, Type)
##    d = difflib.Differ()
##    lara_utils.print_and_flush(f'--- Performing diff...')
##    Diff = d.compare(Seq1, Seq2)
##    lara_utils.print_and_flush(f'... done')
##    Summary = summarise_diff(Diff)
##    lara_utils.write_json_to_file(Summary, OutFile)
##
##def summarise_diff(Diff):
##    return [ Line for Line in list(Diff) if Line[0] in '+-' ]

