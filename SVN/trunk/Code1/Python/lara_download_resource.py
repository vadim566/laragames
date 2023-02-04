import lara_utils

# Download a published LARA resource using the metadata added by lara_add_metadata.add_trivial_metadata_to_directory
def download_resource(URL, TargetDir):
    ( Okay, NFiles, NDirectories ) = download_lara_resource_dir(URL, TargetDir)
    lara_utils.print_and_flush(f'--- Downloaded resource from {URL} to {TargetDir} ({NFiles} files and {NDirectories} directories)')
    return Okay

def download_lara_resource_dir(URL, TargetDir):
    lara_utils.create_directory_deleting_old_if_necessary(TargetDir)
    TrivialMetadataURL = f'{URL}/trivial_metadata.json'
    TrivialMetadataFile = f'{TargetDir}/trivial_metadata.json'
    if not lara_utils.read_file_from_url(TrivialMetadataURL, TrivialMetadataFile):
        lara_utils.print_and_flush(f'*** Warning: unable to download metadata from {TrivialMetadataURL}')
        return ( False, 0, 0 )
    TrivialMetadata = lara_utils.read_json_file(TrivialMetadataFile)
    if not TrivialMetadata or not 'files' in TrivialMetadata or not 'directories' in TrivialMetadata:
        lara_utils.print_and_flush(f'*** Error: metadata downloaded from {TrivialMetadataURL} is not wellformed')
        return False
    ( Okay, NFiles, NDirectories ) = ( True, 0, 1 )
    for File in TrivialMetadata['files']:
        Result = lara_utils.read_file_from_url(f'{URL}/{File}', f'{TargetDir}/{File}')
        if not Result:
            lara_utils.print_and_flush(f'*** Warning: unable to download file from {URL}/{File}')
            Okay = False
        else:
            NFiles += 1
    for Dir in TrivialMetadata['directories']:
        ( Okay1, NFiles1, NDirectories1 ) = download_lara_resource_dir(f'{URL}/{Dir}', f'{TargetDir}/{Dir}')
        if not Okay1:
            Okay = False
        NFiles += NFiles1
        NDirectories += NDirectories1
    return ( Okay, NFiles, NDirectories )


