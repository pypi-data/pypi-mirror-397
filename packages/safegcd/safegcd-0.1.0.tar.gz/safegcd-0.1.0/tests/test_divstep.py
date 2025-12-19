from safegcd import divstep

def test_even_g():
    assert divstep(1, 7, 10) == (3, 7, 5)

def test_odd_delta_neg():
    assert divstep(-1, 7, 9) == (1, 7, 8)

def test_odd_delta_nonneg():
    assert divstep(0, 7, 9) == (2, 9, 1)

