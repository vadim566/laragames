labelled_corpus:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py make_labelled_corpus local_config.json

correct_accents_and_hashtags:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py correct_accents_and_hashtags local_config.json

cut_up_audio_ch1:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch1	
cut_up_audio_ch12a:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12a	
cut_up_audio_ch12b:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12b	
cut_up_audio_ch12c1:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12c1
cut_up_audio_ch12c2:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12c2	
cut_up_audio_ch12d:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12d	
cut_up_audio_ch12e:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12e	
cut_up_audio_ch12f:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12f	
cut_up_audio_ch12g:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12g	
cut_up_audio_ch12h:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12h	
cut_up_audio_ch12i:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch12i	
cut_up_audio_ch13:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch13	
cut_up_audio_ch14:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch14	
cut_up_audio_ch15:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch15	
cut_up_audio_ch16:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch16
cut_up_audio_ch17:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch17
cut_up_audio_ch18:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch18
cut_up_audio_ch19:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch19
cut_up_audio_ch20:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch20
cut_up_audio_ch21:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch21
cut_up_audio_ch22:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch22
cut_up_audio_ch23:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch23
cut_up_audio_ch24:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch24
cut_up_audio_ch25:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch25
cut_up_audio_ch26:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch26
cut_up_audio_ch27:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch27
cut_up_audio_ch28:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py cut_up_audio local_config.json ch28

word_audio_alignment_metadata:
	${MAKE} resources
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_alignment_file local_config.json

cut_up_audio_words:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py align_word_audio local_config.json

trim_audio:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py trim_sentence_audio local_config.json
	${MAKE} copy_embedded_audio_to_trimmed

copy_embedded_audio_to_trimmed:
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch18_4506.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch18_4508.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch20_4923.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch20_4925.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch22_5308.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch22_5310.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch24_5601.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch26_5975.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch26_5977.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch28_6314.mp3 pitjantjatjara_voice_trimmed
	cd ../audio; cp pitjantjatjara_voice/extracted_file_ch28_6316.mp3 pitjantjatjara_voice_trimmed

token_translations_file:
	${PYTHON3} ${LARA}/Code/Python/lara_run_for_portal.py tokens_from_types_and_copy local_config.json ${LARA}/Content/pitjantjatjara_course/translations/pitjantjatjara_english_

resources:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config.json
resources_cover:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_cover.json
resources_1_and_2:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_cover_1_and_2.json
resources_cover_filtered:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_cover_filtered.json
resources_all_stories:
	${MAKE} resources_story_18
	${MAKE} resources_story_20
	${MAKE} resources_story_22
	${MAKE} resources_story_24
	${MAKE} resources_story_26
	${MAKE} resources_story_28
resources_story_18:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_18.json
resources_story_20:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_20.json
resources_story_22:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_22.json
resources_story_24:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_24.json
resources_story_26:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_26.json
resources_story_28:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py resources local_config_story_28.json

word_pages:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config.json
word_pages_cover:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_cover.json
word_pages_1_and_2:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_cover_1_and_2.json
word_pages_cover_filtered:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_cover_filtered.json
word_pages_all_stories:
	${MAKE} word_pages_story_18
	${MAKE} word_pages_story_20
	${MAKE} word_pages_story_22
	${MAKE} word_pages_story_24
	${MAKE} word_pages_story_26
	${MAKE} word_pages_story_28
word_pages_story_18:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_18.json
word_pages_story_20:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_20.json
word_pages_story_22:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_22.json
word_pages_story_24:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_24.json
word_pages_story_26:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_26.json
word_pages_story_28:
	${PYTHON3} ${LARA}/Code/Python/lara_run.py word_pages local_config_story_28.json

tarball:
	cd ${LARA}/compiled ; tar czvf pitjantjatjara_course.tar.gz pitjantjatjara_coursevocabpages
tarball_cover:
	cd ${LARA}/compiled ; tar czvf pitjantjatjara_course_cover.tar.gz pitjantjatjara_course_cleanedvocabpages
tarball_1_and_2:
	cd ${LARA}/compiled ; tar czvf pitjantjatjara_courses_1_and_2.tar.gz pitjantjatjara_courses_1_and_2vocabpages
tarball_packaged:
	cd ${LARA}/packaged ; tar czvf pitjantjatjara_elementary_course_packaged.tar.gz pitjantjatjara_elementary_course
tarball_audio:
	cd ${LARA}/Content/pitjantjatjara_course/audio ; tar czvf pitjantjatjara_course_audio.tar.gz pitjantjatjara_voice_trimmed_filtered

scp_tarball:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_course.tar.gz manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_tarball_cover:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_course_cover.tar.gz manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_tarball_1_and_2:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_courses_1_and_2.tar.gz manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_tarball_packaged:
	cd ${LARA}/packaged ; scp -r pitjantjatjara_elementary_course_packaged.tar.gz manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_tarball_audio:
	cd ${LARA}/Content/pitjantjatjara_course/audio ; scp -r pitjantjatjara_course_audio.tar.gz manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector

scp_all_stories:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_*vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector

scp_story_18:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_18vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_story_20:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_20vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_story_22:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_22vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_story_24:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_24vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_story_26:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_26vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
scp_story_28:
	cd ${LARA}/compiled ; scp -r pitjantjatjara_story_28vocabpages manny@isslnx1.unige.ch:/export/data/www/issco-site/en/research/projects/callector
