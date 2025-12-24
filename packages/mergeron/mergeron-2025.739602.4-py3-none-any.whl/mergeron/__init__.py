"""Variables, types, objects and functions used throughout the package."""

from __future__ import annotations

import enum
from collections.abc import Mapping, Sequence
from multiprocessing import cpu_count
from pathlib import Path
from types import MappingProxyType
from typing import Any

import attrs
import mpmath  # type: ignore
import numpy as np
import numpy.dtypes
from mpmath import mpf
from numpy.typing import DTypeLike, NDArray
from ruamel import yaml

_PKG_NAME: str = Path(__file__).parent.name

VERSION = "2025.739504.0"

__version__ = VERSION

WORK_DIR = globals().get("WORK_DIR", Path.home() / _PKG_NAME)
"""
If defined, the global variable WORK_DIR is used as a data store.

If the user does not define WORK_DIR, a subdirectory in
the user's home directory, named for this package, is
created/reused.
"""
if not WORK_DIR.is_dir():
    WORK_DIR.mkdir(parents=False)

DEFAULT_REC = globals().get("DEFAULT_REC", 0.85)
"""Default recapture rate.

Can be overridden at the user's specification.
Overriding the default recapture rate requires that
this object is redefined **before** instantiating any classes
or calling any functions that invoke this object.
"""

DEFAULT_REP = globals().get("DEFAULT_REP", 0.85)
"""Default replacement rate.

Can be overridden at the user's specification.
Overriding the default recapture rate **requires**
this object be redefined **before** instantiating
any classes or calling any functions that invoke
this object.
"""

NTHREADS = 2 * cpu_count()

type MPFloat = mpmath.ctx_mp_python.mpf
type MPMatrix = mpmath.matrices.matrices._matrix

np.set_printoptions(precision=28, floatmode="fixed", legacy=False)
this_yaml = yaml.YAML(typ="rt")
this_yaml.indent(mapping=2, sequence=4, offset=2)


# https://stackoverflow.com/questions/54611992/
# https://numpy.org/doc/stable/user/basics.subclassing.html#basics-subclassing
@this_yaml.register_class
class PubYear(int):
    """
    Type definition for Guidelines publication year.

    We restrict to publication years Guidelines in which the Agencies indicate
    the use of concentration screens for unilateral competitive effects from
    horizontal mergers.
    """

    def __new__(cls, _y: int) -> PubYear:
        """Raise ValueError if argument not match a Guidelines publication year."""
        if _y not in {1992, 2010, 2023}:
            raise ValueError(
                f"Value given, {_y} is not a valid Guidelines publication year here."
            )
        return super().__new__(cls, _y)

    @classmethod
    def to_yaml(
        cls, _r: yaml.representer.RoundTripRepresenter, _d: PubYear
    ) -> yaml.ScalarNode:
        """Serialize PubYear."""
        return _r.represent_scalar(f"!{cls.__name__}", f"{_d}")

    @classmethod
    def from_yaml(
        cls, _c: yaml.constructor.RoundTripConstructor, _n: yaml.ScalarNode
    ) -> PubYear:
        """Deserialize PubYear."""
        return cls(int(_n.value))


# redefine numpy testing functions to modify default tolerances
def allclose(
    _a: ArrayFloat | ArrayINT | float | int,
    _b: ArrayFloat | ArrayINT | float | int,
    /,
    *,
    rtol: float = 1e-14,
    atol: float = 1e-15,
    equal_nan: bool = True,
) -> bool:
    """Redefine native numpy function with updated default tolerances."""
    return np.allclose(_a, _b, atol=atol, rtol=rtol, equal_nan=equal_nan)


def assert_allclose(  # noqa: PLR0913
    _a: ArrayFloat | ArrayINT | float | int,
    _b: ArrayFloat | ArrayINT | float | int,
    /,
    *,
    rtol: float = 1e-14,
    atol: float = 1e-15,
    equal_nan: bool = True,
    err_msg: str = "",
    verbose: bool = False,
    strict: bool = True,
) -> None:
    """Redefine native numpy function with updated default tolerances, type-enforcing."""
    return np.testing.assert_allclose(
        _a,
        _b,
        atol=atol,
        rtol=rtol,
        equal_nan=equal_nan,
        err_msg=err_msg,
        verbose=verbose,
        strict=True,
    )


# https://numpy.org/devdocs/user/basics.subclassing.html#slightly-more-realistic-example-attribute-added-to-existing-array
class _ArrayTyped(np.ndarray):
    def __new__(
        cls,
        _arr: Sequence[bool | float | int | MPFloat] | np.ndarray,
        _type: DTypeLike,  # np.bool_ | np.float64 | np.floating | np.int64 | np.integer,
        /,
        *,
        info: dict[str, Any] | None = None,
    ) -> _ArrayTyped:
        _dtype_dict: dict[DTypeLike, DTypeLike] = {
            np.bool_: bool,
            np.floating: float,
            np.integer: int,
        }
        _dtype = object if _type == mpf else _dtype_dict.get(_type, _type)

        if not isinstance(_arr, np.ndarray):
            _arr = np.asarray(_arr, _dtype)
        if not np.issubdtype(_arr.dtype, _type):
            raise ValueError(
                f"Array dytpe, {_arr.dtype!r}, is not subtype of target dtype, {_type}."
            )
        obj = np.asarray(_arr, _dtype).view(cls)
        obj.info = info
        return obj

    def __array_finalize__(self, obj: np.ndarray | None) -> None:  # noqa: PLW3201
        if obj is None:
            return
        self.info = getattr(obj, "info", None)
        return


class ArrayBoolean(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[bool] | NDArray[np.bool_]) -> ArrayBoolean:  # noqa: D102
        return _ArrayTyped(_arr, np.bool_).view(cls)


class ArrayDouble(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[float] | NDArray[np.float64]) -> ArrayDouble:  # noqa: D102
        return _ArrayTyped(_arr, np.float64).view(cls)


class ArrayFloat(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[float] | NDArray[np.floating]) -> ArrayFloat:  # noqa: D102
        return _ArrayTyped(_arr, np.floating).view(cls)


class ArrayBIGINT(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[int] | NDArray[np.int64]) -> ArrayBIGINT:  # noqa: D102
        return _ArrayTyped(_arr, np.int64).view(cls)


class ArrayINT(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[int] | NDArray[np.integer]) -> ArrayINT:  # noqa: D102
        return _ArrayTyped(_arr, np.integer).view(cls)


class ArrayMPFloat(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: Sequence[MPFloat] | np.ndarray) -> ArrayMPFloat:  # noqa: D102  # type: ignore
        if not hasattr(next(np.asarray(_arr).flat), "mpf_convert_arg"):
            raise ValueError("Data array cannot be converted to ArrayMPFloat.")
        return _ArrayTyped(_arr, np.object_).view(cls)


class ArrayUINT8(np.ndarray):  # noqa: D101
    def __new__(cls, _arr: NDArray[np.uint8]) -> ArrayUINT8:  # noqa: D102
        return _ArrayTyped(_arr, np.uint8).view(cls)


EMPTY_ARRAYBIGINT = ArrayBIGINT(np.array([], int))
EMPTY_ARRAYDOUBLE = ArrayDouble(np.array([], float))
EMPTY_ARRAYUINT8 = ArrayUINT8(np.array([], np.uint8))
TYPED_ARRAY_MAP: dict[str, type] = {}


# Add functions for serializing/deserializing some objects used
# or defined in this package

# Add yaml representer, constructor for various types
# NoneType
(_, _) = (
    this_yaml.representer.add_representer(
        type(None), lambda _r, _d: _r.represent_scalar("!None", "none")
    ),
    this_yaml.constructor.add_constructor("!None", lambda _c, _n, /: None),
)

# mappingproxytype
_, _ = (
    this_yaml.representer.add_representer(
        MappingProxyType,
        lambda _r, _d: _r.represent_mapping("!mappingproxy", dict(_d.items())),
    ),
    this_yaml.constructor.add_constructor(
        "!mappingproxy", lambda _c, _n: MappingProxyType(dict(**yaml_rt_mapper(_c, _n)))
    ),
)

# mpmpath.mpf
(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.mpf, lambda _r, _d: _r.represent_scalar("!MPFloat", f"{_d}")
    ),
    this_yaml.constructor.add_constructor(
        "!MPFloat", lambda _c, _n, /: mpmath.mpf(_c.construct_scalar(_n))
    ),
)

# mpmath.matrix
(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.matrix, lambda _r, _d: _r.represent_sequence("!MPMatrix", _d.tolist())
    ),
    this_yaml.constructor.add_constructor(
        "!MPMatrix",
        lambda _c, _n, /: mpmath.matrix(_c.construct_sequence(_n, deep=True)),
    ),
)

# Add yaml representer, constructor for ndarray
(_, _) = (
    this_yaml.representer.add_representer(
        np.ndarray,
        lambda _r, _d: _r.represent_sequence("!ndarray", (_d.tolist(), _d.dtype.str)),
    ),
    this_yaml.constructor.add_constructor(
        "!ndarray", lambda _c, _n, /: np.array(*_c.construct_sequence(_n, deep=True))
    ),
)


def yamelize_typed_array(
    _typ: type, /, *, typed_array_map: dict[str, type] = TYPED_ARRAY_MAP
) -> None:
    """Add yaml representer, constructor for attrs-defined class.

    Attributes with property, `init=False` are not serialized/deserialized
    to YAML by the functions defined here. These attributes can, of course,
    be dumped to stand-alone (YAML) representation, and deserialized from there.
    """
    if not _typ.__name__.startswith("Array"):
        raise ValueError(f"Object {_typ} is not typed array.")

    _typ_tag = f"!{_typ.__name__}"

    typed_array_map |= {_typ_tag: _typ}

    _ = this_yaml.representer.add_representer(
        _typ,
        lambda _r, _d: _r.represent_sequence(_typ_tag, (_d.tolist(), _d.dtype.str)),
    )
    _ = this_yaml.constructor.add_constructor(
        _typ_tag,
        lambda _c, _n, /: np.array(*_c.construct_sequence(_n, deep=True)).view(
            typed_array_map[_n.tag]
        ),
    )


for _typ in (
    ArrayBoolean,
    ArrayDouble,
    ArrayFloat,
    ArrayBIGINT,
    ArrayINT,
    ArrayMPFloat,
    ArrayUINT8,
):
    yamelize_typed_array(_typ)


def yaml_rt_mapper(
    _c: yaml.constructor.RoundTripConstructor, _n: yaml.MappingNode
) -> Mapping[str, Any]:
    """Construct mapping from a mapping node with the RoundTripConstructor."""
    data_: Mapping[str, Any] = yaml.constructor.CommentedMap()
    _c.construct_mapping(_n, maptyp=data_, deep=True)
    return data_


PKG_ATTRS_MAP: dict[str, type] = {}


def yamelize_attrs(_typ: type, /, *, attr_map: dict[str, type] = PKG_ATTRS_MAP) -> None:
    """Add yaml representer, constructor for attrs-defined class.

    Attributes with property, `init=False` are not serialized/deserialized
    to YAML by the functions defined here. These attributes can, of course,
    be dumped to stand-alone (YAML) representation, and deserialized from there.
    """
    if not attrs.has(_typ):
        raise ValueError(f"Object {_typ} is not attrs-defined")

    _typ_tag = f"!{_typ.__name__}"
    attr_map |= {_typ_tag: _typ}

    _ = this_yaml.representer.add_representer(
        _typ,
        lambda _r, _d: _r.represent_mapping(
            _typ_tag,
            {_a.name: getattr(_d, _a.name) for _a in _d.__attrs_attrs__ if _a.init},
        ),
    )
    _ = this_yaml.constructor.add_constructor(
        _typ_tag, lambda _c, _n: attr_map[_typ_tag](**yaml_rt_mapper(_c, _n))
    )


@this_yaml.register_class
class Enameled(enum.Enum):
    """Add YAML representer, constructor for enum.Enum."""

    @classmethod
    def to_yaml(
        cls, _r: yaml.representer.RoundTripRepresenter, _d: enum.Enum
    ) -> yaml.ScalarNode:
        """Serialize enumerations by .name, not .value."""
        return _r.represent_scalar(
            f"!{super().__getattribute__(cls, '__name__')}", f"{_d.name}"
        )

    @classmethod
    def from_yaml(
        cls, _c: yaml.constructor.RoundTripConstructor, _n: yaml.ScalarNode
    ) -> enum.EnumType:
        """Deserialize enumeration serialized by .name."""
        retval: enum.EnumType = super().__getattribute__(cls, _n.value)
        return retval


@this_yaml.register_class
@enum.unique
class RECForm(str, Enameled):
    R"""For derivation of recapture rate from market shares.

    With :math:`\mathscr{N}` a set of firms, each supplying a
    single differentiated product, and :math:`\mathscr{M} \subset \mathscr{N}`
    a putative relevant product market, with
    :math:`d_{ij}` denoting diversion ratio from good :math:`i` to good :math:`j`,
    :math:`s_i` denoting market shares, and
    :math:`\overline{r}` the default market recapture rate,
    market recapture rates for the respective products may be specified
    as having one of the following forms:
    """

    FIXED = "fixed"
    R"""Given, :math:`\overline{r}`,

    .. math::

        REC_i = \overline{r} {\ } \forall {\ } i \in \mathscr{M}

    """

    INOUT = "inside-out"
    R"""
    Given, :math:`\overline{r}, s_i {\ } \forall {\ } i \in \mathscr{M}`, with
    :math:`s_{min} = \min(s_1, s_2)`,

    .. math::

        REC_i = \frac{\overline{r} (1 - s_i)}{1 - (1 - \overline{r}) s_{min} - \overline{r} s_i}
        {\ } \forall {\ } i \in \mathscr{M}

    """

    OUTIN = "outside-in"
    R"""
    Given, :math:`d_{ij} {\ } \forall {\ } i, j \in \mathscr{M}, i \neq j`,

    .. math::

        REC_i = {\sum_{j \in \mathscr{M}}^{j \neq i} d_{ij}}
        {\ } \forall {\ } i \in \mathscr{M}

    """


@this_yaml.register_class
@enum.unique
class UPPAggrSelector(str, Enameled):
    """Aggregator for GUPPI and diversion ratio estimates."""

    AVG = "average"
    CPA = "cross-product-share weighted average"
    CPD = "cross-product-share weighted distance"
    CPG = "cross-product-share weighted geometric mean"
    DIS = "symmetrically-weighted distance"
    GMN = "geometric mean"
    MAX = "max"
    MIN = "min"
    OSA = "own-share weighted average"
    OSD = "own-share weighted distance"
    OSG = "own-share weighted geometric mean"
