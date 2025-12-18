/*
 * typepack C extension using PyBytesWriter API (PEP 782)
 *
 * This module provides high-performance binary serialization
 * using Python 3.15+ PyBytesWriter C API for efficient byte buffer management.
 *
 * For Python < 3.15, the pure Python implementation is used as fallback.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Check for PyBytesWriter availability (Python 3.15+) */
#if PY_VERSION_HEX >= 0x030F0000
#define HAVE_PYBYTESWRITER 1
#else
#define HAVE_PYBYTESWRITER 0
#endif

/* MessagePack format markers */
#define MP_NONE      0xC0
#define MP_FALSE     0xC2
#define MP_TRUE      0xC3
#define MP_BIN8      0xC4
#define MP_BIN16     0xC5
#define MP_BIN32     0xC6
#define MP_FLOAT32   0xCA
#define MP_FLOAT64   0xCB
#define MP_UINT8     0xCC
#define MP_UINT16    0xCD
#define MP_UINT32    0xCE
#define MP_UINT64    0xCF
#define MP_INT8      0xD0
#define MP_INT16     0xD1
#define MP_INT32     0xD2
#define MP_INT64     0xD3
#define MP_STR8      0xD9
#define MP_STR16     0xDA
#define MP_STR32     0xDB
#define MP_ARRAY16   0xDC
#define MP_ARRAY32   0xDD
#define MP_MAP16     0xDE
#define MP_MAP32     0xDF

/* Extension type markers */
#define MP_FIXEXT1   0xD4
#define MP_FIXEXT2   0xD5
#define MP_FIXEXT4   0xD6
#define MP_FIXEXT8   0xD7
#define MP_FIXEXT16  0xD8
#define MP_EXT8      0xC7
#define MP_EXT16     0xC8
#define MP_EXT32     0xC9

/* Custom extension type codes */
#define EXT_DATETIME    0x01
#define EXT_DATE        0x02
#define EXT_TIME        0x03
#define EXT_TIMEDELTA   0x04
#define EXT_DECIMAL     0x05
#define EXT_UUID        0x06
#define EXT_SET         0x07
#define EXT_TUPLE       0x08
#define EXT_FROZENSET   0x09
#define EXT_ENUM        0x0A
#define EXT_DATACLASS   0x0B
#define EXT_NAMEDTUPLE  0x0C
#define EXT_CUSTOM      0x0D

/* Helper macros for big-endian encoding */
#define WRITE_BE16(buf, val) do { \
    (buf)[0] = (uint8_t)((val) >> 8); \
    (buf)[1] = (uint8_t)(val); \
} while(0)

#define WRITE_BE32(buf, val) do { \
    (buf)[0] = (uint8_t)((val) >> 24); \
    (buf)[1] = (uint8_t)((val) >> 16); \
    (buf)[2] = (uint8_t)((val) >> 8); \
    (buf)[3] = (uint8_t)(val); \
} while(0)

#define WRITE_BE64(buf, val) do { \
    (buf)[0] = (uint8_t)((val) >> 56); \
    (buf)[1] = (uint8_t)((val) >> 48); \
    (buf)[2] = (uint8_t)((val) >> 40); \
    (buf)[3] = (uint8_t)((val) >> 32); \
    (buf)[4] = (uint8_t)((val) >> 24); \
    (buf)[5] = (uint8_t)((val) >> 16); \
    (buf)[6] = (uint8_t)((val) >> 8); \
    (buf)[7] = (uint8_t)(val); \
} while(0)

/* Helper macros for big-endian decoding */
#define READ_BE16(buf) \
    (((uint16_t)(buf)[0] << 8) | (uint16_t)(buf)[1])

#define READ_BE32(buf) \
    (((uint32_t)(buf)[0] << 24) | ((uint32_t)(buf)[1] << 16) | \
     ((uint32_t)(buf)[2] << 8) | (uint32_t)(buf)[3])

#define READ_BE64(buf) \
    (((uint64_t)(buf)[0] << 56) | ((uint64_t)(buf)[1] << 48) | \
     ((uint64_t)(buf)[2] << 40) | ((uint64_t)(buf)[3] << 32) | \
     ((uint64_t)(buf)[4] << 24) | ((uint64_t)(buf)[5] << 16) | \
     ((uint64_t)(buf)[6] << 8) | (uint64_t)(buf)[7])


#if HAVE_PYBYTESWRITER

/*
 * Pack implementation using PyBytesWriter (Python 3.15+)
 */

/* Forward declarations */
static int pack_value(PyBytesWriter *writer, PyObject *obj);
static int pack_int(PyBytesWriter *writer, PyObject *obj);
static int pack_float(PyBytesWriter *writer, PyObject *obj);
static int pack_str(PyBytesWriter *writer, PyObject *obj);
static int pack_bytes(PyBytesWriter *writer, PyObject *obj);
static int pack_list(PyBytesWriter *writer, PyObject *obj);
static int pack_dict(PyBytesWriter *writer, PyObject *obj);


static int
pack_int(PyBytesWriter *writer, PyObject *obj)
{
    int overflow;
    long long val = PyLong_AsLongLongAndOverflow(obj, &overflow);

    if (overflow == 0 && !PyErr_Occurred()) {
        uint8_t buf[9];

        /* Positive fixint (0-127) */
        if (val >= 0 && val <= 127) {
            buf[0] = (uint8_t)val;
            return PyBytesWriter_WriteBytes(writer, buf, 1);
        }
        /* Negative fixint (-32 to -1) */
        if (val >= -32 && val < 0) {
            buf[0] = (uint8_t)(val & 0xFF);
            return PyBytesWriter_WriteBytes(writer, buf, 1);
        }
        /* uint8 */
        if (val >= 0 && val <= 0xFF) {
            buf[0] = MP_UINT8;
            buf[1] = (uint8_t)val;
            return PyBytesWriter_WriteBytes(writer, buf, 2);
        }
        /* uint16 */
        if (val >= 0 && val <= 0xFFFF) {
            buf[0] = MP_UINT16;
            WRITE_BE16(buf + 1, (uint16_t)val);
            return PyBytesWriter_WriteBytes(writer, buf, 3);
        }
        /* uint32 */
        if (val >= 0 && val <= 0xFFFFFFFF) {
            buf[0] = MP_UINT32;
            WRITE_BE32(buf + 1, (uint32_t)val);
            return PyBytesWriter_WriteBytes(writer, buf, 5);
        }
        /* uint64 */
        if (val >= 0) {
            buf[0] = MP_UINT64;
            WRITE_BE64(buf + 1, (uint64_t)val);
            return PyBytesWriter_WriteBytes(writer, buf, 9);
        }
        /* int8 */
        if (val >= -128) {
            buf[0] = MP_INT8;
            buf[1] = (uint8_t)(int8_t)val;
            return PyBytesWriter_WriteBytes(writer, buf, 2);
        }
        /* int16 */
        if (val >= -32768) {
            buf[0] = MP_INT16;
            WRITE_BE16(buf + 1, (uint16_t)(int16_t)val);
            return PyBytesWriter_WriteBytes(writer, buf, 3);
        }
        /* int32 */
        if (val >= -2147483648LL) {
            buf[0] = MP_INT32;
            WRITE_BE32(buf + 1, (uint32_t)(int32_t)val);
            return PyBytesWriter_WriteBytes(writer, buf, 5);
        }
        /* int64 */
        buf[0] = MP_INT64;
        WRITE_BE64(buf + 1, (uint64_t)val);
        return PyBytesWriter_WriteBytes(writer, buf, 9);
    }

    /* Handle overflow - try unsigned long long */
    PyErr_Clear();
    unsigned long long uval = PyLong_AsUnsignedLongLong(obj);
    if (!PyErr_Occurred()) {
        uint8_t buf[9];
        buf[0] = MP_UINT64;
        WRITE_BE64(buf + 1, uval);
        return PyBytesWriter_WriteBytes(writer, buf, 9);
    }

    PyErr_SetString(PyExc_OverflowError, "Integer too large to pack");
    return -1;
}


static int
pack_float(PyBytesWriter *writer, PyObject *obj)
{
    double val = PyFloat_AS_DOUBLE(obj);
    uint8_t buf[9];
    union {
        double d;
        uint64_t i;
    } u;

    u.d = val;
    buf[0] = MP_FLOAT64;
    WRITE_BE64(buf + 1, u.i);
    return PyBytesWriter_WriteBytes(writer, buf, 9);
}


static int
pack_str(PyBytesWriter *writer, PyObject *obj)
{
    Py_ssize_t size;
    const char *data = PyUnicode_AsUTF8AndSize(obj, &size);
    if (data == NULL) {
        return -1;
    }

    uint8_t header[5];
    Py_ssize_t header_size;

    if (size <= 31) {
        /* Fixstr */
        header[0] = 0xA0 | (uint8_t)size;
        header_size = 1;
    }
    else if (size <= 0xFF) {
        header[0] = MP_STR8;
        header[1] = (uint8_t)size;
        header_size = 2;
    }
    else if (size <= 0xFFFF) {
        header[0] = MP_STR16;
        WRITE_BE16(header + 1, (uint16_t)size);
        header_size = 3;
    }
    else {
        header[0] = MP_STR32;
        WRITE_BE32(header + 1, (uint32_t)size);
        header_size = 5;
    }

    if (PyBytesWriter_WriteBytes(writer, header, header_size) < 0) {
        return -1;
    }
    return PyBytesWriter_WriteBytes(writer, data, size);
}


static int
pack_bytes(PyBytesWriter *writer, PyObject *obj)
{
    Py_ssize_t size = PyBytes_GET_SIZE(obj);
    const char *data = PyBytes_AS_STRING(obj);

    uint8_t header[5];
    Py_ssize_t header_size;

    if (size <= 0xFF) {
        header[0] = MP_BIN8;
        header[1] = (uint8_t)size;
        header_size = 2;
    }
    else if (size <= 0xFFFF) {
        header[0] = MP_BIN16;
        WRITE_BE16(header + 1, (uint16_t)size);
        header_size = 3;
    }
    else {
        header[0] = MP_BIN32;
        WRITE_BE32(header + 1, (uint32_t)size);
        header_size = 5;
    }

    if (PyBytesWriter_WriteBytes(writer, header, header_size) < 0) {
        return -1;
    }
    return PyBytesWriter_WriteBytes(writer, data, size);
}


static int
pack_list(PyBytesWriter *writer, PyObject *obj)
{
    Py_ssize_t size = PyList_GET_SIZE(obj);
    uint8_t header[5];
    Py_ssize_t header_size;

    if (size <= 15) {
        /* Fixarray */
        header[0] = 0x90 | (uint8_t)size;
        header_size = 1;
    }
    else if (size <= 0xFFFF) {
        header[0] = MP_ARRAY16;
        WRITE_BE16(header + 1, (uint16_t)size);
        header_size = 3;
    }
    else {
        header[0] = MP_ARRAY32;
        WRITE_BE32(header + 1, (uint32_t)size);
        header_size = 5;
    }

    if (PyBytesWriter_WriteBytes(writer, header, header_size) < 0) {
        return -1;
    }

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *item = PyList_GET_ITEM(obj, i);
        if (pack_value(writer, item) < 0) {
            return -1;
        }
    }

    return 0;
}


static int
pack_dict(PyBytesWriter *writer, PyObject *obj)
{
    Py_ssize_t size = PyDict_Size(obj);
    uint8_t header[5];
    Py_ssize_t header_size;

    if (size <= 15) {
        /* Fixmap */
        header[0] = 0x80 | (uint8_t)size;
        header_size = 1;
    }
    else if (size <= 0xFFFF) {
        header[0] = MP_MAP16;
        WRITE_BE16(header + 1, (uint16_t)size);
        header_size = 3;
    }
    else {
        header[0] = MP_MAP32;
        WRITE_BE32(header + 1, (uint32_t)size);
        header_size = 5;
    }

    if (PyBytesWriter_WriteBytes(writer, header, header_size) < 0) {
        return -1;
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(obj, &pos, &key, &value)) {
        if (pack_value(writer, key) < 0) {
            return -1;
        }
        if (pack_value(writer, value) < 0) {
            return -1;
        }
    }

    return 0;
}


static int
pack_value(PyBytesWriter *writer, PyObject *obj)
{
    uint8_t marker;

    /* None */
    if (obj == Py_None) {
        marker = MP_NONE;
        return PyBytesWriter_WriteBytes(writer, &marker, 1);
    }

    /* Bool (must check before int, since bool is subclass of int) */
    if (PyBool_Check(obj)) {
        marker = (obj == Py_True) ? MP_TRUE : MP_FALSE;
        return PyBytesWriter_WriteBytes(writer, &marker, 1);
    }

    /* Int */
    if (PyLong_Check(obj)) {
        return pack_int(writer, obj);
    }

    /* Float */
    if (PyFloat_Check(obj)) {
        return pack_float(writer, obj);
    }

    /* String */
    if (PyUnicode_Check(obj)) {
        return pack_str(writer, obj);
    }

    /* Bytes */
    if (PyBytes_Check(obj)) {
        return pack_bytes(writer, obj);
    }

    /* List */
    if (PyList_Check(obj)) {
        return pack_list(writer, obj);
    }

    /* Dict */
    if (PyDict_Check(obj)) {
        return pack_dict(writer, obj);
    }

    /* Tuple - convert to list for now */
    if (PyTuple_Check(obj)) {
        PyObject *list = PySequence_List(obj);
        if (list == NULL) {
            return -1;
        }
        int result = pack_list(writer, list);
        Py_DECREF(list);
        return result;
    }

    PyErr_Format(PyExc_TypeError,
                 "Unsupported type for pack: %.100s",
                 Py_TYPE(obj)->tp_name);
    return -1;
}


static PyObject *
typepack_pack(PyObject *self, PyObject *args)
{
    PyObject *obj;

    if (!PyArg_ParseTuple(args, "O:pack", &obj)) {
        return NULL;
    }

    PyBytesWriter *writer = PyBytesWriter_Create(64);  /* Initial buffer size */
    if (writer == NULL) {
        return NULL;
    }

    if (pack_value(writer, obj) < 0) {
        PyBytesWriter_Discard(writer);
        return NULL;
    }

    return PyBytesWriter_Finish(writer);
}


#else /* !HAVE_PYBYTESWRITER */

/*
 * Fallback for Python < 3.15: Use bytearray
 */

static PyObject *
typepack_pack(PyObject *self, PyObject *args)
{
    /* Import and call the Python implementation */
    PyObject *core_module = PyImport_ImportModule("typepack.core");
    if (core_module == NULL) {
        return NULL;
    }

    PyObject *pack_func = PyObject_GetAttrString(core_module, "pack");
    Py_DECREF(core_module);
    if (pack_func == NULL) {
        return NULL;
    }

    PyObject *result = PyObject_Call(pack_func, args, NULL);
    Py_DECREF(pack_func);
    return result;
}

#endif /* HAVE_PYBYTESWRITER */


/*
 * Unpack implementation (works on all Python versions)
 */

typedef struct {
    const uint8_t *data;
    Py_ssize_t size;
    Py_ssize_t offset;
} UnpackState;


static PyObject *unpack_value(UnpackState *state);


static PyObject *
unpack_str(UnpackState *state, Py_ssize_t length)
{
    if (state->offset + length > state->size) {
        PyErr_SetString(PyExc_ValueError, "Unexpected end of data");
        return NULL;
    }

    PyObject *result = PyUnicode_FromStringAndSize(
        (const char *)(state->data + state->offset), length);
    state->offset += length;
    return result;
}


static PyObject *
unpack_array(UnpackState *state, Py_ssize_t length)
{
    PyObject *result = PyList_New(length);
    if (result == NULL) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject *item = unpack_value(state);
        if (item == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, item);
    }

    return result;
}


static PyObject *
unpack_map(UnpackState *state, Py_ssize_t length)
{
    PyObject *result = PyDict_New();
    if (result == NULL) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject *key = unpack_value(state);
        if (key == NULL) {
            Py_DECREF(result);
            return NULL;
        }

        PyObject *value = unpack_value(state);
        if (value == NULL) {
            Py_DECREF(key);
            Py_DECREF(result);
            return NULL;
        }

        if (PyDict_SetItem(result, key, value) < 0) {
            Py_DECREF(key);
            Py_DECREF(value);
            Py_DECREF(result);
            return NULL;
        }

        Py_DECREF(key);
        Py_DECREF(value);
    }

    return result;
}


static PyObject *
unpack_value(UnpackState *state)
{
    if (state->offset >= state->size) {
        PyErr_SetString(PyExc_ValueError, "Unexpected end of data");
        return NULL;
    }

    uint8_t marker = state->data[state->offset++];

    /* Positive fixint (0x00 - 0x7F) */
    if (marker <= 0x7F) {
        return PyLong_FromLong(marker);
    }

    /* Fixmap (0x80 - 0x8F) */
    if (marker >= 0x80 && marker <= 0x8F) {
        Py_ssize_t length = marker & 0x0F;
        return unpack_map(state, length);
    }

    /* Fixarray (0x90 - 0x9F) */
    if (marker >= 0x90 && marker <= 0x9F) {
        Py_ssize_t length = marker & 0x0F;
        return unpack_array(state, length);
    }

    /* Fixstr (0xA0 - 0xBF) */
    if (marker >= 0xA0 && marker <= 0xBF) {
        Py_ssize_t length = marker & 0x1F;
        return unpack_str(state, length);
    }

    /* Negative fixint (0xE0 - 0xFF) */
    if (marker >= 0xE0) {
        return PyLong_FromLong((int8_t)marker);
    }

    /* None */
    if (marker == MP_NONE) {
        Py_RETURN_NONE;
    }

    /* False */
    if (marker == MP_FALSE) {
        Py_RETURN_FALSE;
    }

    /* True */
    if (marker == MP_TRUE) {
        Py_RETURN_TRUE;
    }

    /* Binary */
    if (marker == MP_BIN8) {
        if (state->offset >= state->size) goto error;
        Py_ssize_t length = state->data[state->offset++];
        if (state->offset + length > state->size) goto error;
        PyObject *result = PyBytes_FromStringAndSize(
            (const char *)(state->data + state->offset), length);
        state->offset += length;
        return result;
    }
    if (marker == MP_BIN16) {
        if (state->offset + 2 > state->size) goto error;
        Py_ssize_t length = READ_BE16(state->data + state->offset);
        state->offset += 2;
        if (state->offset + length > state->size) goto error;
        PyObject *result = PyBytes_FromStringAndSize(
            (const char *)(state->data + state->offset), length);
        state->offset += length;
        return result;
    }
    if (marker == MP_BIN32) {
        if (state->offset + 4 > state->size) goto error;
        Py_ssize_t length = READ_BE32(state->data + state->offset);
        state->offset += 4;
        if (state->offset + length > state->size) goto error;
        PyObject *result = PyBytes_FromStringAndSize(
            (const char *)(state->data + state->offset), length);
        state->offset += length;
        return result;
    }

    /* Float */
    if (marker == MP_FLOAT32) {
        if (state->offset + 4 > state->size) goto error;
        union { float f; uint32_t i; } u;
        u.i = READ_BE32(state->data + state->offset);
        state->offset += 4;
        return PyFloat_FromDouble(u.f);
    }
    if (marker == MP_FLOAT64) {
        if (state->offset + 8 > state->size) goto error;
        union { double d; uint64_t i; } u;
        u.i = READ_BE64(state->data + state->offset);
        state->offset += 8;
        return PyFloat_FromDouble(u.d);
    }

    /* Unsigned integers */
    if (marker == MP_UINT8) {
        if (state->offset >= state->size) goto error;
        return PyLong_FromUnsignedLong(state->data[state->offset++]);
    }
    if (marker == MP_UINT16) {
        if (state->offset + 2 > state->size) goto error;
        uint16_t val = READ_BE16(state->data + state->offset);
        state->offset += 2;
        return PyLong_FromUnsignedLong(val);
    }
    if (marker == MP_UINT32) {
        if (state->offset + 4 > state->size) goto error;
        uint32_t val = READ_BE32(state->data + state->offset);
        state->offset += 4;
        return PyLong_FromUnsignedLong(val);
    }
    if (marker == MP_UINT64) {
        if (state->offset + 8 > state->size) goto error;
        uint64_t val = READ_BE64(state->data + state->offset);
        state->offset += 8;
        return PyLong_FromUnsignedLongLong(val);
    }

    /* Signed integers */
    if (marker == MP_INT8) {
        if (state->offset >= state->size) goto error;
        return PyLong_FromLong((int8_t)state->data[state->offset++]);
    }
    if (marker == MP_INT16) {
        if (state->offset + 2 > state->size) goto error;
        int16_t val = (int16_t)READ_BE16(state->data + state->offset);
        state->offset += 2;
        return PyLong_FromLong(val);
    }
    if (marker == MP_INT32) {
        if (state->offset + 4 > state->size) goto error;
        int32_t val = (int32_t)READ_BE32(state->data + state->offset);
        state->offset += 4;
        return PyLong_FromLong(val);
    }
    if (marker == MP_INT64) {
        if (state->offset + 8 > state->size) goto error;
        int64_t val = (int64_t)READ_BE64(state->data + state->offset);
        state->offset += 8;
        return PyLong_FromLongLong(val);
    }

    /* Strings */
    if (marker == MP_STR8) {
        if (state->offset >= state->size) goto error;
        Py_ssize_t length = state->data[state->offset++];
        return unpack_str(state, length);
    }
    if (marker == MP_STR16) {
        if (state->offset + 2 > state->size) goto error;
        Py_ssize_t length = READ_BE16(state->data + state->offset);
        state->offset += 2;
        return unpack_str(state, length);
    }
    if (marker == MP_STR32) {
        if (state->offset + 4 > state->size) goto error;
        Py_ssize_t length = READ_BE32(state->data + state->offset);
        state->offset += 4;
        return unpack_str(state, length);
    }

    /* Arrays */
    if (marker == MP_ARRAY16) {
        if (state->offset + 2 > state->size) goto error;
        Py_ssize_t length = READ_BE16(state->data + state->offset);
        state->offset += 2;
        return unpack_array(state, length);
    }
    if (marker == MP_ARRAY32) {
        if (state->offset + 4 > state->size) goto error;
        Py_ssize_t length = READ_BE32(state->data + state->offset);
        state->offset += 4;
        return unpack_array(state, length);
    }

    /* Maps */
    if (marker == MP_MAP16) {
        if (state->offset + 2 > state->size) goto error;
        Py_ssize_t length = READ_BE16(state->data + state->offset);
        state->offset += 2;
        return unpack_map(state, length);
    }
    if (marker == MP_MAP32) {
        if (state->offset + 4 > state->size) goto error;
        Py_ssize_t length = READ_BE32(state->data + state->offset);
        state->offset += 4;
        return unpack_map(state, length);
    }

    PyErr_Format(PyExc_ValueError, "Unknown format marker: 0x%02X", marker);
    return NULL;

error:
    PyErr_SetString(PyExc_ValueError, "Unexpected end of data");
    return NULL;
}


static PyObject *
typepack_unpack(PyObject *self, PyObject *args)
{
    Py_buffer buffer;

    if (!PyArg_ParseTuple(args, "y*:unpack", &buffer)) {
        return NULL;
    }

    UnpackState state = {
        .data = (const uint8_t *)buffer.buf,
        .size = buffer.len,
        .offset = 0
    };

    PyObject *result = unpack_value(&state);
    PyBuffer_Release(&buffer);
    return result;
}


/*
 * Check if C extension has PyBytesWriter support
 */
static PyObject *
typepack_has_pybyteswriter(PyObject *self, PyObject *Py_UNUSED(args))
{
#if HAVE_PYBYTESWRITER
    Py_RETURN_TRUE;
#else
    Py_RETURN_FALSE;
#endif
}


/*
 * Module definition
 */

static PyMethodDef typepack_methods[] = {
    {"pack", typepack_pack, METH_VARARGS,
     "Serialize a Python object to binary format."},
    {"unpack", typepack_unpack, METH_VARARGS,
     "Deserialize binary data to a Python object."},
    {"has_pybyteswriter", typepack_has_pybyteswriter, METH_NOARGS,
     "Return True if compiled with PyBytesWriter support (Python 3.15+)."},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef typepack_module = {
    PyModuleDef_HEAD_INIT,
    "_typepack",
    "Fast binary serialization C extension",
    -1,
    typepack_methods
};


PyMODINIT_FUNC
PyInit__typepack(void)
{
    return PyModule_Create(&typepack_module);
}
