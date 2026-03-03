import nbformat
import numpy as np
import pytest
from pathlib import Path


NOTEBOOK_NAME = "numpy_programming_exercises.ipynb"


def load_student_namespace():
    """
    Loads only imports + function definitions from the notebook into a namespace.
    This avoids running demo/print cells while still getting the student's functions.
    """
    nb_path = Path(__file__).resolve().parents[1] / NOTEBOOK_NAME
    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found at: {nb_path}")

    nb = nbformat.read(nb_path, as_version=4)

    ns = {"np": np}

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        src = cell.source.strip()
        if not src:
            continue

        # Run numpy import cells (common patterns)
        if "import numpy" in src or src.startswith("import ") or src.startswith("from "):
            exec(src, ns)

        # Run cells that define functions
        if "def " in src:
            exec(src, ns)

    return ns


@pytest.fixture(scope="session")
def student():
    ns = load_student_namespace()
    required = [
        "split_vertically",
        "split_horizontally",
        "split_and_merge_vertically",
        "split_and_merge_horizontally",
        "rotate_array",
        "create_array",
        "evaluate",
    ]
    missing = [f for f in required if f not in ns]
    if missing:
        raise AssertionError(f"Missing required functions in notebook: {missing}")
    return ns


def test_split_vertically(student):
    a = np.arange(12).reshape(4, 3)
    top, bottom = student["split_vertically"](a, 2)
    assert np.array_equal(top, a[:2, :])
    assert np.array_equal(bottom, a[2:, :])


def test_split_horizontally(student):
    a = np.arange(12).reshape(3, 4)
    left, right = student["split_horizontally"](a, 2)
    assert np.array_equal(left, a[:, :2])
    assert np.array_equal(right, a[:, 2:])


def test_split_and_merge_vertically(student):
    a1 = np.arange(20).reshape(5, 4)
    a2 = (np.arange(20) + 100).reshape(5, 4)

    arr1, arr2 = student["split_and_merge_vertically"](a1, a2, 2, 3)

    expected1 = np.vstack((a1[:2, :], a2[3:, :]))
    expected2 = np.vstack((a2[:3, :], a1[2:, :]))

    assert np.array_equal(arr1, expected1)
    assert np.array_equal(arr2, expected2)


def test_split_and_merge_horizontally(student):
    a1 = np.arange(20).reshape(5, 4)
    a2 = (np.arange(20) + 100).reshape(5, 4)

    arr1, arr2 = student["split_and_merge_horizontally"](a1, a2, 1, 3)

    expected1 = np.hstack((a1[:, :1], a2[:, 3:]))
    expected2 = np.hstack((a2[:, :3], a1[:, 1:]))

    assert np.array_equal(arr1, expected1)
    assert np.array_equal(arr2, expected2)


def test_rotate_array(student):
    a = np.array([[1, 2], [3, 4], [5, 6]])
    out = student["rotate_array"](a, shift_right_by=2, target_shape=(3, 2))

    flat = np.ravel(a)
    expected = np.roll(flat, 2).reshape(3, 2)
    assert np.array_equal(out, expected)


def test_rotate_array_empty(student):
    a = np.array([])
    out = student["rotate_array"](a, shift_right_by=3, target_shape=(0,))
    assert out.shape == (0,)


def test_create_array_int_cast(student):
    # all integer start/stop -> should cast to int in the reference behavior
    out = student["create_array"](m=2, n=5, values=[(0, 4), (10, 14)])
    assert out.dtype.kind in ("i", "u")  # int/uint
    assert np.array_equal(out[0], np.array([0, 1, 2, 3, 4]))
    assert np.array_equal(out[1], np.array([10, 11, 12, 13, 14]))


def test_create_array_float(student):
    # any float start/stop -> should stay float
    out = student["create_array"](m=1, n=4, values=[(0.0, 1.0)])
    assert out.dtype.kind == "f"
    assert np.allclose(out[0], np.linspace(0.0, 1.0, 4))


def test_evaluate_basic_ops(student):
    # sequential ops: (([1,2,3] + 2) * 3) => [9,12,15]
    operands = [np.array([1, 2, 3]), 2, 3]
    operators = ["+", "*"]
    out = student["evaluate"](operands, operators)
    assert np.array_equal(out, np.array([9, 12, 15]))


def test_evaluate_unary_ops(student):
    operands = [np.array([1.0, 4.0, 9.0])]
    operators = ["sqrt"]
    out = student["evaluate"](operands, operators)
    assert np.allclose(out, np.array([1.0, 2.0, 3.0]))


def test_evaluate_errors(student):
    with pytest.raises(ValueError):
        student["evaluate"]([1], ["+"])  # missing rhs operand
