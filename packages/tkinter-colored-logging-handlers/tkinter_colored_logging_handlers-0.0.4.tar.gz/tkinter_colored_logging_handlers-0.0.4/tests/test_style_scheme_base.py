from tkinter_colored_logging_handlers import StyleScheme, StyleSchemeBase


class TestStyleSchemeBaseCheck:
    def test_check_runs_without_error(self, capsys):
        StyleSchemeBase.check()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_check_outputs_correct_range(self, capsys):
        StyleSchemeBase.check()
        captured = capsys.readouterr()
        output = captured.out
        for i in range(1, 150):
            assert f"[{i}]" in output


class TestStyleSchemeBaseToDict:
    def test_to_dict_returns_dict(self):
        result = StyleScheme.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_tuples(self):
        result = StyleScheme.to_dict()
        assert len(result) > 0
        for value in result.values():
            assert isinstance(value, tuple)
            assert len(value) == 3

    def test_to_dict_has_font_attributes(self):
        result = StyleScheme.to_dict()
        expected_keys = ["BOLD", "ITALIC", "UNDERLINE"]
        for key in expected_keys:
            assert key in result

    def test_to_dict_has_color_attributes(self):
        result = StyleScheme.to_dict()
        expected_keys = ["BLACK", "RED", "GREEN"]
        for key in expected_keys:
            assert key in result

    def test_to_dict_excludes_private_attributes(self):
        result = StyleScheme.to_dict()
        for key in result.keys():
            assert not key.startswith("_")
