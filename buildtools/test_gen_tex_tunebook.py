#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest

from abcparser import demote_determinant
from gen_tex_tunebook import *

# unittest reminder:
# assert functions: assertEqual(), assertRaises() and assert_(condition)

class TestTuneIndex(unittest.TestCase):

    def test_format_tune_index_entry(self):
        tune = Tune("Come Upstairs with Me", "slip jig")
        expected_result = "\emph{Come Upstairs with Me}~(slip jig),~p.\pageref{come_upstairs_with_me}"
        self.assertEqual(expected_result, format_index_entry(tune))

    def test_format_tune_index_entry_empty_type(self):
        tune = Tune(title = "Come Upstairs with Me", tune_type="")
        expected_result = "\emph{Come Upstairs with Me},~p.\pageref{come_upstairs_with_me}"
        self.assertEqual(expected_result, format_index_entry(tune))

    def test_format_tune_index_entry_no_type(self):
        tune = Tune(title="Come Upstairs with Me", tune_type=None)
        expected_result = "\emph{Come Upstairs with Me},~p.\pageref{come_upstairs_with_me}"
        self.assertEqual(expected_result, format_index_entry(tune))

    def test_sort_by_name(self):
        tunes = [Tune("Yellow Tinker", "reel"),
                 Tune("Come Upstairs with Me", "slip jig"),
                 Tune("Mistress on the Floor", "reel")]

        tunes.sort()

        self.assertEqual([Tune("Come Upstairs with Me", "slip jig"),
                          Tune("Mistress on the Floor", "reel"),
                          Tune("Yellow Tinker", "reel")], tunes)

    def test_demote_determinant(self):
        self.assertEqual("Yellow Tinker, The", demote_determinant("The Yellow Tinker"))

    def test_demote_determinant_2(self):
        self.assertEqual("Ridées de Lanvaudan, Les",
                         demote_determinant("Les Ridées de Lanvaudan"))

    def test_dont_demote_determinant(self):
        self.assertEqual("Then I Go", demote_determinant("Then I Go"))

    def test_dont_demote_determinant_2(self):
        self.assertEqual("", demote_determinant(""))

    def prepare_exception_text(self, before, after):
        text = "The sorted list differs from the expected sorted list\n"
        text += "Expected sorted list:\n"
        for tune in before:
            text += "    " + str(tune) + "\n"
        text += "Actual sorted list:\n"
        for tune in after:
            text += "    " + str(tune) + "\n"
        return text

    def test_sort_by_name_demote_determinant(self):
        tunes = [Tune("The Humours of Whiskey", "slip jig"),
                 Tune("Come Upstairs with Me", "slip jig"),
                 Tune("Mistress on the Floor", "reel")]

        tunes.sort()

        expected_sorted_tunes = [Tune("Come Upstairs with Me", "slip jig"),
                                 Tune("Humours of Whiskey, The", "slip jig"),
                                 Tune("Mistress on the Floor", "reel")]

        self.assertEqual(expected_sorted_tunes, tunes,
                         self.prepare_exception_text(expected_sorted_tunes, tunes))

    def test_gen_index_of_tunes(self):
        tunes = [Tune("The Humours of Whiskey", "slip jig"),
                 Tune("Come Upstairs with Me", "slip jig"),
                 Tune("Toss the Feathers", "reel"),
                 Tune("Mistress on the Floor", "reel")]

        latex_index = gen_index_of_tunes(tunes)

        expected_latex_index = r"""\section*{Index des airs}
\emph{Come Upstairs with Me}~(slip jig),~p.\pageref{come_upstairs_with_me}

\emph{Humours of Whiskey, The}~(slip jig),~p.\pageref{the_humours_of_whiskey}

\emph{Mistress on the Floor}~(reel),~p.\pageref{mistress_on_the_floor}

\emph{Toss the Feathers}~(reel),~p.\pageref{toss_the_feathers}

"""

        self.assertEqual(expected_latex_index, latex_index)


class TestFormatSetIndexEntry(unittest.TestCase):

    def test_set_index_entry(self):
        tunes = [Tune(title="Our Kate", tune_type="slow air"),
                 Tune("Unnamed Jig 2", "jig"),
                 Tune("Paddy Fahy's", "reel")]
        expected_index_entry = r"""\emph{Our Kate}~(slow air,~p.\pageref{our_kate})~/ \emph{Unnamed Jig 2}~(jig,~p.\pageref{unnamed_jig_2})~/ \emph{Paddy Fahy's}~(reel,~p.\pageref{paddy_fahy_s})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_no_type(self):
        # One entry without type
        tunes = [Tune("Our Kate", "slow air"),
                 Tune("The Mysterious Tune")]
        expected_index_entry = r"""\emph{Our Kate}~(slow air,~p.\pageref{our_kate})~/ \emph{The Mysterious Tune}~(p.\pageref{the_mysterious_tune})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_no_type2(self):
        # One entry without type
        tunes = [Tune("Our Kate", "slow air"),
                 Tune("The Mysterious Tune", None)]
        expected_index_entry = r"""\emph{Our Kate}~(slow air,~p.\pageref{our_kate})~/ \emph{The Mysterious Tune}~(p.\pageref{the_mysterious_tune})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_factorize_type(self):
        # All the entries have the same type
        tunes = [Tune("The Mountain Road", "reel"),
                 Tune("The Twelve Pins", "reel")]
        expected_index_entry = r"""Reels: \emph{The Mountain Road}~(p.\pageref{the_mountain_road})~/ \emph{The Twelve Pins}~(p.\pageref{the_twelve_pins})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_no_type_at_all(self):
        # Factorization does not apply here
        tunes = [Tune("Our Kate", None),
                 Tune("The Mysterious Tune", None)]
        expected_index_entry = r"""\emph{Our Kate}~(p.\pageref{our_kate})~/ \emph{The Mysterious Tune}~(p.\pageref{the_mysterious_tune})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_only_one_tune(self):
        # One entry without type
        tunes = [Tune("Our Kate", "slow air")]
        expected_index_entry = r"""\emph{Our Kate}~(slow air,~p.\pageref{our_kate})"""

        index_entry = format_set_index_entry(tunes)

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_with_title(self):
        tunes = [Tune("Our Kate", "slow air"),
                 Tune("Unnamed Jig 2", "jig"),
                 Tune("Paddy Fahy's", "reel")]
        expected_index_entry = r"""\emph{The Old Set}: \emph{Our Kate}~(slow air,~p.\pageref{our_kate})~/ \emph{Unnamed Jig 2}~(jig,~p.\pageref{unnamed_jig_2})~/ \emph{Paddy Fahy's}~(reel,~p.\pageref{paddy_fahy_s})"""

        index_entry = format_set_index_entry(tunes, "The Old Set")

        self.assertEqual(expected_index_entry, index_entry)

    def test_set_index_entry_factorize_type_with_title(self):
        # All the entries have the same type
        tunes = [Tune("The Mountain Road", "reel"),
                 Tune("The Twelve Pins", "reel")]
        expected_index_entry = r"""\emph{The Snowy Set} (reels): \emph{The Mountain Road}~(p.\pageref{the_mountain_road})~/ \emph{The Twelve Pins}~(p.\pageref{the_twelve_pins})"""

        index_entry = format_set_index_entry(tunes, "The Snowy Set")

        self.assertEqual(expected_index_entry, index_entry)



class TestParseSet(unittest.TestCase):

    def test_split_title_and_tunes(self):
        index_entry = "The Oran Set: les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel"
        (title_for_index, index_tunes) = split_title_and_tunes(index_entry)
        self.assertEqual("The Oran Set", title_for_index)
        self.assertEqual("les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel", index_tunes)

    def test_split_title_and_tunes_no_title(self):
        index_entry = "les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel"
        (title_for_index, index_tunes) = split_title_and_tunes(index_entry)
        self.assertEqual("", title_for_index)
        self.assertEqual("les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel", index_tunes)

    def test_split_title_and_tunes_no_title_spurious_spaces(self):
        index_entry = "   les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel   "
        (title_for_index, index_tunes) = split_title_and_tunes(index_entry)
        self.assertEqual("", title_for_index)
        self.assertEqual("les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel", index_tunes)

    def test_split_title_and_tunes_empty_title(self):
        index_entry = "    :les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel"
        (title_for_index, index_tunes) = split_title_and_tunes(index_entry)
        self.assertEqual("", title_for_index)
        self.assertEqual("les_ridees_de_lanvaudan, union_street_session, the_rolling_waves_of_frehel", index_tunes)

    def test_split_title_and_tunes_no_tune(self):
        index_entry = "The Oran Set:"
        (title_for_index, index_tunes) = split_title_and_tunes(index_entry)
        self.assertEqual("The Oran Set", title_for_index)
        self.assertEqual("", index_tunes)


if __name__ == '__main__':
    unittest.main()

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestCurrent)
    #unittest.TextTestRunner(verbosity=2).run(suite)
