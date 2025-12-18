from peliqan.utils import canonicalize_identifier


def test_canonicalize_identifier():
    test_cases = [
        ("asda\"'.", "asda___"),
        ("As_mf", "as_mf"),
        ("Ömer Hayyam", "ömer_hayyam"),
        ("Pøstmark", "pøstmark"),
    ]
    for test_case in test_cases:
        result = canonicalize_identifier(test_case[0])
        assert result == test_case[1]
