import pytest


def titles(cards):
	return sorted(card.title for card in cards)


# --- basic name search (accent-insensitive) -------------------------------

def test_search_cards_accent_insensitive(sotm):
	# Unaccented query finds the accented card name.
	assert titles(sotm.search_cards("la capitan")) == ["La Capitán"]


def test_search_cards_accented_query(sotm):
	# Accented query works too.
	assert titles(sotm.search_cards("la capitán")) == ["La Capitán"]


def test_search_cards_substring(sotm):
	# "pl" appears in both "Plunder" and "Plummeting Monorail" (across different decks).
	assert titles(sotm.search_cards("pl")) == ["Plummeting Monorail", "Plunder"]


def test_search_cards_no_match(sotm):
	assert list(sotm.search_cards("nonexistent")) == []


def test_search_cards_deck_hint_filters(sotm):
	# The card lives in the "La Capitán" deck, not Megalopolis.
	assert titles(sotm.search_cards("la capitan", deck_hint="megalopolis")) == []
	assert titles(sotm.search_cards("la capitan", deck_hint="la capitan")) == ["La Capitán"]


def test_search_cards_matches_other_side(sotm):
	# Searching by the back-side name returns the merged front card.
	results = sotm.search_cards("backside")
	assert titles(results) == ["Frontside"]
	assert results[0].other_side is not None
	assert results[0].other_side.title == "Backside"


# --- deck / mod search ----------------------------------------------------

def test_search_decks_accent_insensitive(sotm):
	decks = sotm.search_decks("la capitan")
	assert [d.name for d in decks] == ["La Capitán"]


def test_search_mods(sotm):
	mods = sotm.search_mods("cauldron")
	assert [m.name for m in mods] == ["Cauldron"]


# --- advanced search ------------------------------------------------------

def test_advanced_and_across_keys(sotm):
	# Ongoing AND from Cauldron -> only Biofeedback (Captain's Orders is ongoing but not Cauldron).
	results = sotm.search_cards_advanced({"type": ["ongoing"], "mod": ["cauldron"]})
	assert titles(results) == ["Biofeedback"]


def test_advanced_or_within_key(sotm):
	# Ongoing OR One-Shot within the La Capitán deck.
	results = sotm.search_cards_advanced({
		"type": ["ongoing", "one-shot"],
		"deck": ["la capitan"],
	})
	assert titles(results) == ["Captain's Orders", "Plunder"]


def test_advanced_ability_text_search(sotm):
	results = sotm.search_cards_advanced({"ability": ["draw a card"]})
	assert titles(results) == ["Biofeedback"]


def test_advanced_kind(sotm):
	results = sotm.search_cards_advanced({"kind": ["environment"]})
	assert titles(results) == ["Plummeting Monorail"]


def test_advanced_name_matches_other_side(sotm):
	results = sotm.search_cards_advanced({"name": ["backside"]})
	assert titles(results) == ["Frontside"]


def test_advanced_aliases_match_canonical(sotm):
	by_alias = titles(sotm.search_cards_advanced({"type": ["ongoing"]}))
	by_canonical = titles(sotm.search_cards_advanced({"keyword": ["ongoing"]}))
	assert by_alias == by_canonical
	assert "Biofeedback" in by_alias

	by_alias_kind = titles(sotm.search_cards_advanced({"decktype": ["environment"]}))
	by_canonical_kind = titles(sotm.search_cards_advanced({"kind": ["environment"]}))
	assert by_alias_kind == by_canonical_kind


def test_advanced_name_accent_insensitive(sotm):
	assert titles(sotm.search_cards_advanced({"name": ["la capitan"]})) == ["La Capitán"]


def test_advanced_unknown_key_raises(sotm):
	with pytest.raises(sotm.AdvancedSearchError) as excinfo:
		sotm.search_cards_advanced({"colour": ["blue"]})
	# The error should help the user by listing valid keys.
	assert "colour" in str(excinfo.value)
	assert "keyword" in str(excinfo.value)


def test_advanced_empty_criteria_returns_empty(sotm):
	assert list(sotm.search_cards_advanced({})) == []


def test_advanced_empty_values_ignored(sotm):
	# A key whose only value is blank contributes no clause -> no usable criteria.
	assert list(sotm.search_cards_advanced({"name": ["   "]})) == []


# --- formatting -----------------------------------------------------------

def test_format_card_without_magic_numbers(sotm):
	# Regression: cards with no magic_numbers (None) must format without crashing.
	(card,) = sotm.search_cards("la capitan")
	assert card.magic_numbers is None
	rendered = repr(card)  # exercises Card.format via TextFormatter
	assert "La Capitán" in rendered


def test_format_card_with_none_keywords(sotm):
	# keywords can also be None on some cards; formatting must tolerate it.
	(card,) = sotm.search_cards("la capitan")
	card.keywords = None
	repr(card)  # should not raise
