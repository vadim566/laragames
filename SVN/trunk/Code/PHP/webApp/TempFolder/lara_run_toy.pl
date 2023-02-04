:- ensure_loaded('$REGULUS/PrologLib/compatibility').

:- use_module('$REGULUS/PrologLib/utilities').

:- use_module(library(lists)).

%-----------------------------------------------

lara_compile_from_command_line_toy :-
	prolog_flag(argv, Args),
	lara_compile_from_command_line_toy1(Args).

lara_compile_from_command_line_toy1(Args) :-
	get_lara_compile_args_or_complain_toy(Args, Word, MainArgs),
	MainArgs = [File],
	write_word_three_times_to_file(Word, File),
	!.

write_word_three_times_to_file(Word, File) :-
	List = [Word, Word, Word],
	safe_absolute_file_name(File, AbsFile),
	write_atom_list_to_unicode_file(List, AbsFile),
	format('~N--- Output written to "~w"~n', [AbsFile]),
	!.

get_lara_compile_args_or_complain_toy(Args, Word, [File]) :-
	Args = [Word, File],
	!.
get_lara_compile_args_or_complain_toy(_Args, _Word, _MainArgs) :-
	format('~N~nUsage: sicstus -l \'$REGULUS/Prolog/lara_run_toy.pl\' -a <Word> <File>', []),
	fail.

:- lara_compile_from_command_line_toy.

:- halt.
