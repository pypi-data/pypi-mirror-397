from trame import TrameBuilder


def get_trame_from_test(filename):
    return TrameBuilder.from_file(f"src/trame_tests/data/{filename}")
