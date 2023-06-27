from .generic import *

class AleoID(Sized, Serialize, Deserialize, metaclass=ABCMeta):
    size = 32

    def __init__(self, data):
        if not isinstance(self._prefix, str):
            raise TypeError("locator_prefix must be str")
        if len(self._prefix) != 2:
            raise ValueError("locator_prefix must be 2 bytes")
        self.data = data

    @property
    @abstractmethod
    def _prefix(self):
        raise NotImplementedError

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, bytes):
            raise TypeError("data must be bytes")
        self._data = value
        self._bech32m = Bech32m(value, self._prefix)

    def dump(self) -> bytes:
        return self._data

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        if len(data) < cls.size:
            raise ValueError("incorrect length")
        size = cls.size
        self = cls(bytes(data[:size]))
        del data[:size]
        return self

    @classmethod
    # @type_check
    def loads(cls, data: str):
        hrp, data = aleo.bech32_decode(data)
        if hrp != cls._prefix:
            raise ValueError("incorrect hrp")
        if len(data) != cls.size:
            raise ValueError("incorrect length")
        return cls(bytes(data))

    def __str__(self):
        return str(self._bech32m)

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self) + ")"

    def __eq__(self, other):
        if not isinstance(other, AleoID):
            return False
        return self.data == other.data


class AleoObject(Sized, Serialize, Deserialize, metaclass=ABCMeta):
    def __init__(self, data):
        if not isinstance(self._prefix, str):
            raise TypeError("object_prefix must be str")
        # if len(self._prefix) != 4:
        #     raise ValueError("object_prefix must be 4 bytes")
        self.data = data

    @property
    @abstractmethod
    def _prefix(self):
        raise NotImplementedError

    size: int

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, bytes):
            raise TypeError("data must be bytes")
        if len(value) != self.size:
            raise ValueError("data must be %d bytes" % self.size)
        self._data = value
        self._bech32m = Bech32m(value, self._prefix)

    def dump(self) -> bytes:
        return self._data

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        size = cls.size
        # noinspection PyTypeChecker
        if len(data) < size:
            raise ValueError("incorrect length")
        self = cls(bytes(data[:size]))
        del data[:size]
        return self

    @classmethod
    # @type_check
    def loads(cls, data: str):
        hrp, data = aleo.bech32_decode(data)
        if hrp != cls._prefix:
            raise ValueError("incorrect hrp")
        if len(data) != cls.size:
            raise ValueError("incorrect length")
        return cls(bytes(data))

    def __str__(self):
        return str(self._bech32m)

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self) + ")"

    def __eq__(self, other):
        if not isinstance(other, AleoObject):
            return False
        return self.data == other.data


class BlockHash(AleoID):
    _prefix = "ab"


class StateRoot(AleoID):
    _prefix = "ar"


class TransactionID(AleoID):
    _prefix = "at"


class TransitionID(AleoID):
    _prefix = "as"


## Saved for reference
# class RecordCiphertext(AleoObject):
#     _prefix = "recd"
#     size = 288
#
#     def __init__(self, data):
#         AleoObject.__init__(self, data)
#
#     def get_commitment(self):
#         return aleo.get_record_ciphertext_commitment(self.data)


class Address(AleoObject):
    # Should work like this...

    _prefix = "aleo"
    size = 32

    def __init__(self, data):
        AleoObject.__init__(self, data)


class Field(Serialize, Deserialize):
    # Fr, Fp256
    # Just store as a large integer now
    # Hopefully this will not be used later...
    # @type_check
    def __init__(self, data):
        if not isinstance(data, int):
            raise TypeError("data must be int")
        self.data = data

    def dump(self) -> bytes:
        return self.data.to_bytes(32, "little")

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        if len(data) < 32:
            raise ValueError("incorrect length")
        data_ = int.from_bytes(bytes(data[:32]), "little")
        del data[:32]
        return cls(data_)

    @classmethod
    def loads(cls, data: str):
        return cls(int(data.removesuffix("field")))

    def __str__(self):
        return str(self.data) + "field"

    def __eq__(self, other):
        if not isinstance(other, Field):
            return False
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    def __add__(self, other):
        if not isinstance(other, Field):
            raise TypeError("other must be Field")
        return Field.load(bytearray(aleo.field_ops(self.dump(), other.dump(), "add")))


class Group(Serialize, Deserialize):
    # This is definitely wrong, but we are not using the internals
    # @type_check
    def __init__(self, data):
        if not isinstance(data, int):
            raise TypeError("data must be int")
        self.data = data

    def dump(self) -> bytes:
        return self.data.to_bytes(32, "little")

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        if len(data) < 32:
            raise ValueError("incorrect length")
        data_ = int.from_bytes(bytes(data[:32]), "little")
        del data[:32]
        return cls(data_)

    @classmethod
    def loads(cls, data: str):
        return cls(int(data.removesuffix("group")))

    def __str__(self):
        return str(self.data) + "group"


class Scalar(Serialize, Deserialize):
    # Could be wrong as well
    # @type_check
    def __init__(self, data):
        if not isinstance(data, int):
            raise TypeError("data must be int")
        self.data = data

    def dump(self) -> bytes:
        return self.data.to_bytes(32, "little")

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        if len(data) < 32:
            raise ValueError("incorrect length")
        data_ = int.from_bytes(bytes(data[:32]), "little")
        del data[:32]
        return cls(data_)

    @classmethod
    def loads(cls, data: str):
        return cls(int(data.removesuffix("scalar")))

    def __str__(self):
        return str(self.data) + "scalar"


class Fq(Serialize, Deserialize):
    # Fp384, G1
    # @type_check
    def __init__(self, value: int):
        self.value = value

    def dump(self) -> bytes:
        return self.value.to_bytes(48, "little")

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        if len(data) < 48:
            raise ValueError("incorrect length")
        value = int.from_bytes(bytes(data[:48]), "little")
        del data[:48]
        return cls(value=value)

    def __str__(self):
        return str(self.value)

class G1Affine(Serialize, Deserialize):

    # @type_check
    def __init__(self, *, x: Fq, flags: bool):
        self.x = x
        self.flags = flags

    def dump(self) -> bytes:
        res = bytearray(self.x.dump())
        res[-1] |= self.flags << 7
        return bytes(res)

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        data_ = data[:48]
        del data[:48]
        flags = bool(data_[-1] >> 7)
        data_[-1] &= 0x7f
        return cls(x=Fq.load(data_), flags=flags)

class Fq2(Serialize, Deserialize):

    # @type_check
    def __init__(self, c0: Fq, c1: Fq, flags: bool):
        self.c0 = c0
        self.c1 = c1
        self.flags = flags

    def dump(self) -> bytes:
        res = bytearray(self.c0.dump() + self.c1.dump())
        res[-1] |= self.flags << 7
        return res

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        data_ = data[:96]
        del data[:96]
        flags = bool(data_[-1] >> 7)
        data_[-1] &= 0x7f
        c0 = Fq.load(data_)
        c1 = Fq.load(data_)
        return cls(c0=c0, c1=c1, flags=flags)

class G2Affine(Serialize, Deserialize):

    # @type_check
    def __init__(self, *, x: Fq2):
        self.x = x

    def dump(self) -> bytes:
        return self.x.dump()

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        x = Fq2.load(data)
        return cls(x=x)

class G2Prepared(Serialize, Deserialize):

    # @type_check
    @generic_type_check
    def __init__(self, *, ell_coeffs: Vec[Tuple[Fq2, Fq2, Fq2], u64], infinity: bool_):
        self.ell_coeffs = ell_coeffs
        self.infinity = infinity

    def dump(self) -> bytes:
        return self.ell_coeffs.dump() + self.infinity.dump()

    @classmethod
    # @type_check
    def load(cls, data: bytearray):
        ell_coeffs = Vec[Tuple[Fq2, Fq2, Fq2], u64].load(data)
        infinity = bool_.load(data)
        return cls(ell_coeffs=ell_coeffs, infinity=infinity)