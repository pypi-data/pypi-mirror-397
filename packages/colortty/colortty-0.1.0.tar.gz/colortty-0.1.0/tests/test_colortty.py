import unittest

from colortty import (
    colortty,
    ColorTTY,
    bold,
    underline,
    sparking,
    inverse,
    invisible,
)


class TestColorTTY(unittest.TestCase):
    def test_basic_fore_and_back_colors(self):
        s = colortty("Hello").set(ColorTTY.Color.red()).set(ColorTTY.BackgroundColor.blue()).make()
        self.assertEqual(s, "\033[31;44mHello\033[0m")

    def test_lighter_variant(self):
        s = colortty("Bright").set(ColorTTY.Color.red(lighter=True)).make()
        self.assertEqual(s, "\033[91mBright\033[0m")

    def test_reusable_statement(self):
        st = colortty().set(ColorTTY.Color.green())
        self.assertEqual(st.make("Go"), "\033[32mGo\033[0m")
        st2 = st.set(ColorTTY.BackgroundColor.white(lighter=True))
        self.assertEqual(st2.make("Go!"), "\033[32;107mGo!\033[0m")

    def test_attributes(self):
        s = (
            colortty("Attr")
            .set(bold())
            .set(underline())
            .set(sparking())
            .set(inverse())
            .set(invisible(False))
            .make()
        )
        # bold(1), underline(4), sparking(5), inverse(7)
        self.assertEqual(s, "\033[1;4;5;7mAttr\033[0m")

    def test_invisible_true(self):
        s = colortty("Hidden").set(invisible(True)).make()
        self.assertEqual(s, "\033[8mHidden\033[0m")

    def test_256_color_index(self):
        s = colortty("Idx").set(ColorTTY.Color.color_256(208)).make()
        # 30 base (foreground), 8 -> 38 (extended), then 5;208 sequence
        self.assertEqual(s, "\033[38;5;208mIdx\033[0m")

    def test_rgb_truecolor(self):
        s = colortty("RGB").set(ColorTTY.Color.color(255, 128, 64)).make()
        # 38;2;r;g;b for foreground truecolor
        self.assertEqual(s, "\033[38;2;255;128;64mRGB\033[0m")

    def test_background_colors(self):
        s = colortty("BG").set(ColorTTY.BackgroundColor.yellow()).make()
        self.assertEqual(s, "\033[43mBG\033[0m")

        s2 = colortty("BG2").set(ColorTTY.BackgroundColor.yellow(lighter=True)).make()
        self.assertEqual(s2, "\033[103mBG2\033[0m")

    def test_statement_str_and_repr(self):
        st = colortty().set(ColorTTY.Color.red())
        # str() with no bound string should return repr-style content
        self.assertTrue(str(st).startswith("<Statement from ColorTTY"))
        # repr contains attributes description
        self.assertIn("Fore: red", repr(st))

        st_bound = colortty("X").set(ColorTTY.Color.blue())
        self.assertEqual(str(st_bound), "\033[34mX\033[0m")

    def test_color_value_errors(self):
        # Invalid 24-bit color mode nibble should raise
        with self.assertRaises(ValueError):
            obj = ColorTTY("bad")
            obj.set_attr(ColorTTY.Mode.Color, 0x38)  # invalid low byte 0x38
            obj.make()

    def test_256_color_wrapping(self):
        # Indices beyond 255 should wrap to low 8 bits: 300 -> 44
        s = colortty("Wrap").set(ColorTTY.Color.color_256(300)).make()
        self.assertEqual(s, "\033[38;5;44mWrap\033[0m")

    def test_make_with_none_string(self):
        st = colortty()
        self.assertEqual(st.make(None), "")

    def test_chaining_order_and_combination(self):
        s = (
            colortty("All")
            .set(ColorTTY.Color.cyan(lighter=True))
            .set(ColorTTY.BackgroundColor.magenta())
            .set(bold())
            .set(underline())
            .make()
        )
        self.assertEqual(s, "\033[96;45;1;4mAll\033[0m")


if __name__ == "__main__":
    unittest.main()
