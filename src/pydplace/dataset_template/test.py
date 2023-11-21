def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_dplace_check(cldf_dataset, cldf_logger):
    pass
