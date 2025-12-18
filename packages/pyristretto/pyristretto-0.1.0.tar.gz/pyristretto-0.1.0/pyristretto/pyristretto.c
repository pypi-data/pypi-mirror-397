#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <sodium.h>
#include <string.h>
#include <stdlib.h>

/* identity */
static unsigned char MODULE_IDENTITY_POINT[32];

/* concat tuple of bytes; caller frees */
static unsigned char *concat_args(PyObject *args_tuple, Py_ssize_t *out_len) {
    Py_ssize_t n = PyTuple_Size(args_tuple);
    Py_ssize_t i;
    size_t total = 0;
    for (i = 0; i < n; ++i) {
        PyObject *it = PyTuple_GetItem(args_tuple, i); /* borrowed */
        if (!PyBytes_Check(it)) {
            PyErr_SetString(PyExc_TypeError, "All arguments must be bytes");
            return NULL;
        }
        total += (size_t)PyBytes_GET_SIZE(it);
    }
    unsigned char *buf = (unsigned char*)malloc(total);
    if (!buf) { PyErr_NoMemory(); return NULL; }
    size_t off = 0;
    for (i = 0; i < n; ++i) {
        PyObject *it = PyTuple_GetItem(args_tuple, i);
        char *data = PyBytes_AS_STRING(it);
        Py_ssize_t len = PyBytes_GET_SIZE(it);
        memcpy(buf + off, data, (size_t)len);
        off += (size_t)len;
    }
    *out_len = (Py_ssize_t)total;
    return buf;
}

/* hash to scalar */
static PyObject* py_Hs(PyObject *self, PyObject *args) {
    if (!PyTuple_Check(args)) {
        PyErr_SetString(PyExc_TypeError, "Hs expects bytes arguments");
        return NULL;
    }
    Py_ssize_t total_len;
    unsigned char *buf = concat_args(args, &total_len);
    if (!buf) return NULL;

    unsigned char h64[64];
    if (crypto_generichash(h64, sizeof(h64), buf, (unsigned long long)total_len, NULL, 0) != 0) {
        free(buf);
        PyErr_SetString(PyExc_RuntimeError, "crypto_generichash failed");
        return NULL;
    }
    free(buf);

    unsigned char scalar32[32];
    crypto_core_ristretto255_scalar_reduce(scalar32, h64);

    // lil endian 32-byte scalar to py int
    PyObject *pyint = _PyLong_FromByteArray(scalar32, 32, 1, 0);
    if (!pyint) {
        PyErr_SetString(PyExc_RuntimeError, "_PyLong_FromByteArray failed");
        return NULL;
    }
    return pyint;
}

/* hash to point */
static PyObject *py_Hp(PyObject *self, PyObject *args)
{
    if (!PyTuple_Check(args)) {
        PyErr_SetString(PyExc_TypeError, "Hp expects bytes arguments");
        return NULL;
    }
    Py_ssize_t total_len;
    unsigned char *buf = concat_args(args, &total_len);
    if (!buf) return NULL;

    unsigned char h64[64];
    int hash_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    hash_rc = crypto_generichash(h64, sizeof(h64), buf, (unsigned long long)total_len, NULL, 0);
    Py_END_ALLOW_THREADS
    if (hash_rc != 0) {
        free(buf);
        PyErr_SetString(PyExc_RuntimeError, "crypto_generichash failed");
        return NULL;
    }
    free(buf);

    unsigned char point[32];
    int fromhash_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    fromhash_rc = crypto_core_ristretto255_from_hash(point, h64);
    Py_END_ALLOW_THREADS
    if (fromhash_rc != 0) {
        PyErr_SetString(PyExc_RuntimeError, "crypto_core_ristretto255_from_hash failed");
        return NULL;
    }
    return PyBytes_FromStringAndSize((const char *)point, 32);
}

/* generator derivations */
static PyObject* py_derive_generators(PyObject *self, PyObject *args) {
    const unsigned char *domain;
    Py_ssize_t domain_len;
    long n;
    if (!PyArg_ParseTuple(args, "y#l", &domain, &domain_len, &n)) return NULL;
    if (n < 0) { PyErr_SetString(PyExc_ValueError, "n must be >= 0"); return NULL; }

    PyObject *list = PyList_New((Py_ssize_t)n);
    if (!list) return NULL;

    /* init state that we'll reuse */
    crypto_generichash_state base_state;
    if (crypto_generichash_init(&base_state, NULL, 0, 64) != 0) {
        Py_DECREF(list);
        PyErr_SetString(PyExc_RuntimeError, "crypto_generichash_init failed");
        return NULL;
    }
    if (domain_len > 0) {
        if (crypto_generichash_update(&base_state, domain, (unsigned long long)domain_len) != 0) {
            Py_DECREF(list);
            PyErr_SetString(PyExc_RuntimeError, "crypto_generichash_update failed");
            return NULL;
        }
    }

    for (long i = 0; i < n; ++i) {
        crypto_generichash_state st = base_state; /* struct copy */

        unsigned char counter[4];
        counter[0] = (unsigned char)(i & 0xff);
        counter[1] = (unsigned char)((i >> 8) & 0xff);
        counter[2] = (unsigned char)((i >> 16) & 0xff);
        counter[3] = (unsigned char)((i >> 24) & 0xff);

        unsigned char h64[64];
        int update_rc = 0;
        int final_rc = 0;
        int fromhash_rc = 0;
        unsigned char point[32];

        Py_BEGIN_ALLOW_THREADS
        update_rc = crypto_generichash_update(&st, counter, 4);
        if (update_rc == 0) {
            final_rc = crypto_generichash_final(&st, h64, 64);
        }
        if (final_rc == 0) {
            fromhash_rc = crypto_core_ristretto255_from_hash(point, h64);
        }
        Py_END_ALLOW_THREADS

        if (update_rc != 0 || final_rc != 0) {
            Py_DECREF(list);
            PyErr_SetString(PyExc_RuntimeError, "crypto_generichash_* failed");
            return NULL;
        }
        if (fromhash_rc != 0) {
            Py_DECREF(list);
            PyErr_SetString(PyExc_RuntimeError, "crypto_core_ristretto255_from_hash failed");
            return NULL;
        }

        PyObject *pybytes = PyBytes_FromStringAndSize((const char*)point, 32);
        if (!pybytes) { Py_DECREF(list); return NULL; }
        PyList_SET_ITEM(list, (Py_ssize_t)i, pybytes); /* steals ref */
    }
    return list;
}

/* adds two points */
static PyObject* py_point_add(PyObject *self, PyObject *args) {
    Py_buffer Pbuf;
    Py_buffer Qbuf;
    memset(&Pbuf, 0, sizeof(Py_buffer));
    memset(&Qbuf, 0, sizeof(Py_buffer));

    if (!PyArg_ParseTuple(args, "y*y*", &Pbuf, &Qbuf)) return NULL;

    /* validate sizes */
    if (Pbuf.len != 32 || Qbuf.len != 32) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_ValueError, "points must be 32 bytes");
        return NULL;
    }

    const unsigned char *P = (const unsigned char*)Pbuf.buf;
    const unsigned char *Q = (const unsigned char*)Qbuf.buf;

    int validP = 0, validQ = 0;
    Py_BEGIN_ALLOW_THREADS
    validP = crypto_core_ristretto255_is_valid_point(P);
    validQ = crypto_core_ristretto255_is_valid_point(Q);
    Py_END_ALLOW_THREADS

    if (!validP || !validQ) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_ValueError, "invalid point(s)");
        return NULL;
    }

    /* identity fast paths */
    if (memcmp(P, MODULE_IDENTITY_POINT, 32) == 0) {
        PyObject *res = PyBytes_FromStringAndSize((const char*)Q, 32);
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        return res;
    }

    if (memcmp(Q, MODULE_IDENTITY_POINT, 32) == 0) {
        PyObject *res = PyBytes_FromStringAndSize((const char*)P, 32);
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        return res;
    }

    unsigned char out[32];
    int add_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    add_rc = crypto_core_ristretto255_add(out, P, Q);
    Py_END_ALLOW_THREADS
    if (add_rc != 0) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_RuntimeError, "add failed");
        return NULL;
    }
    PyBuffer_Release(&Pbuf);
    PyBuffer_Release(&Qbuf);
    return PyBytes_FromStringAndSize((const char*)out, 32);
}

/* subtracts two points */
static PyObject* py_point_sub(PyObject *self, PyObject *args) {
    Py_buffer Pbuf;
    Py_buffer Qbuf;
    memset(&Pbuf, 0, sizeof(Py_buffer));
    memset(&Qbuf, 0, sizeof(Py_buffer));

    if (!PyArg_ParseTuple(args, "y*y*", &Pbuf, &Qbuf)) return NULL;

    // Validate sizes
    if (Pbuf.len != 32 || Qbuf.len != 32) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_ValueError, "points must be 32 bytes");
        return NULL;
    }

    const unsigned char *P = (const unsigned char*)Pbuf.buf;
    const unsigned char *Q = (const unsigned char*)Qbuf.buf;

    int validP = 0, validQ = 0;
    Py_BEGIN_ALLOW_THREADS
    validP = crypto_core_ristretto255_is_valid_point(P);
    validQ = crypto_core_ristretto255_is_valid_point(Q);
    Py_END_ALLOW_THREADS

    if (!validP || !validQ) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_ValueError, "invalid point(s)");
        return NULL;
    }

    // identity fast path: A - 0 = A
    if (memcmp(Q, MODULE_IDENTITY_POINT, 32) == 0) {
        PyObject *res = PyBytes_FromStringAndSize((const char*)P, 32);
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        return res;
    }

    unsigned char out[32];
    int sub_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    sub_rc = crypto_core_ristretto255_sub(out, P, Q);
    Py_END_ALLOW_THREADS
    if (sub_rc != 0) {
        PyBuffer_Release(&Pbuf);
        PyBuffer_Release(&Qbuf);
        PyErr_SetString(PyExc_RuntimeError, "sub failed");
        return NULL;
    }
    PyBuffer_Release(&Pbuf);
    PyBuffer_Release(&Qbuf);
    return PyBytes_FromStringAndSize((const char*)out, 32);
}

/* adds many points */
static PyObject* py_point_sum(PyObject *self, PyObject *args) {
    PyObject *list_obj;
    if (!PyArg_ParseTuple(args, "O", &list_obj)) return NULL;
    if (!PyList_Check(list_obj)) { PyErr_SetString(PyExc_TypeError, "Argument must be a list of points"); return NULL; }
    Py_ssize_t n = PyList_GET_SIZE(list_obj);
    if (n <= 0) { PyErr_SetString(PyExc_ValueError, "empty list"); return NULL; }

    // Start with first item
    PyObject *first = PyList_GET_ITEM(list_obj, 0); // borrowed
    if (!PyBytes_Check(first)) { PyErr_SetString(PyExc_TypeError, "list items must be bytes"); return NULL; }
    const unsigned char *fptr = (const unsigned char*)PyBytes_AS_STRING(first);
    int valid_first = 0;
    Py_BEGIN_ALLOW_THREADS
    valid_first = crypto_core_ristretto255_is_valid_point(fptr);
    Py_END_ALLOW_THREADS
    if (!valid_first) { PyErr_SetString(PyExc_ValueError, "invalid point in list"); return NULL; }
    unsigned char acc[32];
    memcpy(acc, fptr, 32);

    for (Py_ssize_t i = 1; i < n; ++i) {
        PyObject *it = PyList_GET_ITEM(list_obj, i); // borrowed
        if (!PyBytes_Check(it)) { PyErr_SetString(PyExc_TypeError, "list items must be bytes"); return NULL; }
        const unsigned char *p = (const unsigned char*)PyBytes_AS_STRING(it);
        int valid_p = 0;
        Py_BEGIN_ALLOW_THREADS
        valid_p = crypto_core_ristretto255_is_valid_point(p);
        Py_END_ALLOW_THREADS
        if (!valid_p) { PyErr_SetString(PyExc_ValueError, "invalid point in list"); return NULL; }
        if (memcmp(p, MODULE_IDENTITY_POINT, 32) == 0) continue; // skip identity

        unsigned char tmp[32];
        int add_rc = 0;
        Py_BEGIN_ALLOW_THREADS
        add_rc = crypto_core_ristretto255_add(tmp, acc, p);
        Py_END_ALLOW_THREADS
        if (add_rc != 0) { PyErr_SetString(PyExc_RuntimeError, "add failed"); return NULL; }
        memcpy(acc, tmp, 32);
    }
    return PyBytes_FromStringAndSize((const char*)acc, 32);
}

/* converts py int -> 64B lil-endian (signed) buffer then scalar_reduce */
static int pyint_to_reduced_scalar(PyObject *pyint, unsigned char out_scalar32[32]) {
    if (!PyLong_Check(pyint)) { PyErr_SetString(PyExc_TypeError, "expected int"); return -1; }
    unsigned char tmp64[64];
    memset(tmp64, 0, 64);
    if (_PyLong_AsByteArray((PyLongObject*)pyint, tmp64, 64, 1, 1) != 0) {
        PyErr_SetString(PyExc_ValueError, "failed to convert int to bytes");
        return -1;
    }
    crypto_core_ristretto255_scalar_reduce(out_scalar32, tmp64);
    return 0;
}

/* multiplies scalar with point */
static PyObject* py_point_mul(PyObject *self, PyObject *args) {
    PyObject *py_s;
    Py_buffer Pbuf;
    memset(&Pbuf, 0, sizeof(Py_buffer));
    if (!PyArg_ParseTuple(args, "Oy*", &py_s, &Pbuf)) return NULL;

    if (Pbuf.len != 32) {
        PyBuffer_Release(&Pbuf);
        PyErr_SetString(PyExc_ValueError, "point must be 32 bytes");
        return NULL;
    }
    const unsigned char *P = (const unsigned char*)Pbuf.buf;

    int validP = 0;
    Py_BEGIN_ALLOW_THREADS
    validP = crypto_core_ristretto255_is_valid_point(P);
    Py_END_ALLOW_THREADS
    if (!validP) {
        PyBuffer_Release(&Pbuf);
        PyErr_SetString(PyExc_ValueError, "invalid point");
        return NULL;
    }

    unsigned char scalar32[32];
    if (pyint_to_reduced_scalar(py_s, scalar32) != 0) {
        PyBuffer_Release(&Pbuf);
        return NULL;
    }
    /* check zero scalar */
    int all_zero = 1;
    for (int i = 0; i < 32; ++i) if (scalar32[i] != 0) { all_zero = 0; break; }
    if (all_zero) {
        PyBuffer_Release(&Pbuf);
        /* cached identity */
        return PyBytes_FromStringAndSize((const char*)MODULE_IDENTITY_POINT, 32);
    }
    unsigned char out[32];
    int scmul_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    scmul_rc = crypto_scalarmult_ristretto255(out, scalar32, P);
    Py_END_ALLOW_THREADS
    if (scmul_rc != 0) {
        PyBuffer_Release(&Pbuf);
        PyErr_SetString(PyExc_RuntimeError, "scalar mult failed");
        return NULL;
    }
    PyBuffer_Release(&Pbuf);
    return PyBytes_FromStringAndSize((const char*)out, 32);
}

/* multiply scalar by the base point (G) */
static PyObject* py_base_mul(PyObject *self, PyObject *args) {
    PyObject *py_s;
    if (!PyArg_ParseTuple(args, "O", &py_s)) return NULL;
    unsigned char scalar32[32];
    if (pyint_to_reduced_scalar(py_s, scalar32) != 0) return NULL;
    int all_zero = 1;
    for (int i = 0; i < 32; ++i) if (scalar32[i] != 0) { all_zero = 0; break; }
    if (all_zero) {
        return PyBytes_FromStringAndSize((const char*)MODULE_IDENTITY_POINT, 32);
    }
    unsigned char out[32];
    int base_rc = 0;
    Py_BEGIN_ALLOW_THREADS
    base_rc = crypto_scalarmult_ristretto255_base(out, scalar32);
    Py_END_ALLOW_THREADS
    if (base_rc != 0) { PyErr_SetString(PyExc_RuntimeError, "base mult failed"); return NULL; }
    return PyBytes_FromStringAndSize((const char*)out, 32);
}

/* assert if point is invalid, error msg with a name */
static PyObject* py_assert_valid_point(PyObject *self, PyObject *args) {
    const char *name;
    Py_buffer Pbuf;
    memset(&Pbuf, 0, sizeof(Py_buffer));

    if (!PyArg_ParseTuple(args, "sy*", &name, &Pbuf)) {
        return NULL;
    }

    if (Pbuf.len != 32) {
        PyBuffer_Release(&Pbuf);
        PyErr_Format(PyExc_AssertionError,
                     "Invalid Ristretto point (%s): wrong length %zd",
                     name, Pbuf.len);
        return NULL;
    }

    const unsigned char *P = (const unsigned char *)Pbuf.buf;
    int valid = 0;

    Py_BEGIN_ALLOW_THREADS
    valid = crypto_core_ristretto255_is_valid_point(P);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&Pbuf);

    if (!valid) {
        PyErr_Format(PyExc_AssertionError,
                     "Invalid Ristretto point: %s",
                     name);
        return NULL;
    }

    Py_RETURN_NONE;
}

/* return bool if point is valid or not */
static PyObject* py_is_valid_point(PyObject *self, PyObject *args) {
    Py_buffer Pbuf;
    memset(&Pbuf, 0, sizeof(Py_buffer));

    if (!PyArg_ParseTuple(args, "y*", &Pbuf)) {
        return NULL;
    }

    if (Pbuf.len != 32) {
        PyBuffer_Release(&Pbuf);
        Py_RETURN_FALSE;
    }

    const unsigned char *P = (const unsigned char *)Pbuf.buf;
    int valid;

    /* cheap enough so no GIL release */
    valid = crypto_core_ristretto255_is_valid_point(P);

    PyBuffer_Release(&Pbuf);

    if (valid) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/* methods */
static PyMethodDef RistrettoMethods[] = {
    {"Hs", (PyCFunction)py_Hs, METH_VARARGS, "Hs(*args: bytes) -> int: hash -> reduce to scalar"},
    {"Hp", (PyCFunction)py_Hp, METH_VARARGS, "Hp(*args: bytes) -> bytes: hash -> ristretto_from_hash"},
    {"derive_generators", (PyCFunction)py_derive_generators, METH_VARARGS, "derive_generators(domain: bytes, n: int) -> list[bytes]"},
    {"point_add", (PyCFunction)py_point_add, METH_VARARGS, "point_add(P, Q) -> bytes"},
    {"point_sub", (PyCFunction)py_point_sub, METH_VARARGS, "point_sub(P, Q) -> bytes"},
    {"point_sum", (PyCFunction)py_point_sum, METH_VARARGS, "point_sum(list[points]) -> bytes"},
    {"point_mul", (PyCFunction)py_point_mul, METH_VARARGS, "point_mul(scalar, P) -> bytes"},
    {"base_mul", (PyCFunction)py_base_mul, METH_VARARGS, "base_mul(scalar) -> bytes"},
    {"assert_valid_point", (PyCFunction)py_assert_valid_point, METH_VARARGS, "assert_valid_point(name: str, P: bytes) -> None"},
    {"is_valid_point", (PyCFunction)py_is_valid_point, METH_VARARGS, "is_valid_point(P: bytes) -> bool"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pyristretto_module = {
    PyModuleDef_HEAD_INIT,
    "pyristretto",
    "Accelerated Ristretto255 helpers with libsodium",
    -1,
    RistrettoMethods
};

PyMODINIT_FUNC PyInit_pyristretto(void) {
    if (sodium_init() < 0) {
        PyErr_SetString(PyExc_RuntimeError, "sodium_init failed");
        return NULL;
    }

    /* init identity */
    unsigned char zero_scalar[32];
    memset(zero_scalar, 0, 32);
    memset(MODULE_IDENTITY_POINT, 0, 32);

    return PyModule_Create(&pyristretto_module);
}
