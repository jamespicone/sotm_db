from normalize import normalize_for_search


def test_strips_accents():
	assert normalize_for_search("La Capitán") == "la capitan"


def test_folds_case():
	assert normalize_for_search("ONGOING") == "ongoing"


def test_accented_and_plain_collapse_together():
	assert normalize_for_search("La Capitán") == normalize_for_search("la capitan")


def test_casefold_expands_eszett():
	# casefold (unlike lower) turns 'ß' into 'ss'
	assert normalize_for_search("Straße") == "strasse"


def test_none_passes_through():
	assert normalize_for_search(None) is None


def test_empty_string():
	assert normalize_for_search("") == ""


def test_plain_ascii_unchanged():
	assert normalize_for_search("plummeting monorail") == "plummeting monorail"
