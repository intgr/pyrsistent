import pickle
import pytest
from pyrsistent import CheckedPMap, InvariantException, PMap, CheckedType, CheckedPSet, CheckedPVector


class FloatToIntMap(CheckedPMap):
    __key_type__ = float
    __value_type__ = int
    __invariant__ = lambda key, value: (int(key) == value, 'Invalid mapping')

def test_instantiate():
    x = FloatToIntMap({1.25: 1, 2.5: 2})

    assert dict(x.items()) == {1.25: 1, 2.5: 2}
    assert isinstance(x, FloatToIntMap)
    assert isinstance(x, PMap)
    assert isinstance(x, CheckedType)

def test_instantiate_empty():
    x = FloatToIntMap()

    assert dict(x.items()) == {}
    assert isinstance(x, FloatToIntMap)

def test_set():
     x = FloatToIntMap()
     x2 = x.set(1.0, 1)

     assert x2[1.0] == 1
     assert isinstance(x2, FloatToIntMap)

def test_invalid_key_type():
     with pytest.raises(TypeError):
         FloatToIntMap({1: 1})

def test_invalid_value_type():
     with pytest.raises(TypeError):
         FloatToIntMap({1.0: 1.0})

def test_breaking_invariant():
     try:
         FloatToIntMap({1.5: 2})
         assert False
     except InvariantException as e:
        assert e.invariant_errors == ['Invalid mapping']

def test_repr():
    x = FloatToIntMap({1.25: 1})

    assert str(x) == 'FloatToIntMap({1.25: 1})'

def test_default_serialization():
    x = FloatToIntMap({1.25: 1, 2.5: 2})

    assert x.serialize() == {1.25: 1, 2.5: 2}

class StringFloatToIntMap(FloatToIntMap):
    @staticmethod
    def __serializer__(format, key, value):
        return format.format(key), format.format(value)

def test_custom_serialization():
    x = StringFloatToIntMap({1.25: 1, 2.5: 2})

    assert x.serialize("{0}") == {"1.25": "1", "2.5": "2"}

def test_create_non_checked_types():
    assert FloatToIntMap.create({1.25: 1, 2.5: 2}) == FloatToIntMap({1.25: 1, 2.5: 2})

def test_create_checked_types():
    class IntSet(CheckedPSet):
        __type__ = int

    class FloatVector(CheckedPVector):
        __type__ = float

    class IntSetToFloatVectorMap(CheckedPMap):
        __key_type__ = IntSet
        __value_type__ = FloatVector

    x = IntSetToFloatVectorMap.create({frozenset([1, 2]): [1.25, 2.5]})

    assert str(x) == "IntSetToFloatVectorMap({IntSet([1, 2]): FloatVector([1.25, 2.5])})"

def test_evolver_returns_same_instance_when_no_updates():
    x = FloatToIntMap({1.25: 1, 2.25: 2})

    assert x.evolver().persistent() is x

def test_map_with_no_types_or_invariants():
    class NoCheckPMap(CheckedPMap):
        pass

    x = NoCheckPMap({1: 2, 3: 4})
    assert x[1] == 2
    assert x[3] == 4


def test_pickling():
    x = FloatToIntMap({1.25: 1, 2.5: 2})
    y = pickle.loads(pickle.dumps(x, -1))

    assert x == y
    assert isinstance(y, FloatToIntMap)
