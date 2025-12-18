#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <sodium.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/*
 Optimized Naive MSM C extension for Ristretto255 using libsodium.
  - Pre-validate & copy scalars/points while holding the GIL.
  - Reduce scalars to 32 bytes once.
  - Copy point bytes into a contiguous buffer once.
  - Release the GIL for the crypto_scalarmult + add loop.
*/

/* helper: convert python int -> reduced 32-byte scalar
   !!! must be called while holding the GIL !!!
*/
static int py_long_to_reduced32(PyObject *py_long, unsigned char out32[32]) {
    unsigned char tmp64[64];
    memset(tmp64, 0, sizeof(tmp64));

    /* lil endian, signed*/
    if (_PyLong_AsByteArray((PyLongObject *)py_long, tmp64, sizeof(tmp64), 1, 1) < 0) return -1;
    unsigned char reduced[32];
    crypto_core_ristretto255_scalar_reduce(reduced, tmp64);
    memcpy(out32, reduced, 32);
    return 0;
}

static PyObject *msm(PyObject *self, PyObject *args) {
    PyObject *py_scalars = NULL;
    PyObject *py_points = NULL;

    if (!PyArg_ParseTuple(args, "OO", &py_scalars, &py_points)) {
        return NULL;
    }

    /* convert to fast sequence */
    PyObject *scalars_seq = PySequence_Fast(py_scalars, "scalars must be a sequence");
    if (scalars_seq == NULL) return NULL;
    PyObject *points_seq = PySequence_Fast(py_points, "points must be a sequence");
    if (points_seq == NULL) {
        Py_DECREF(scalars_seq);
        return NULL;
    }

    /* some sanity checks */
    Py_ssize_t n = PySequence_Fast_GET_SIZE(scalars_seq);
    if (n != PySequence_Fast_GET_SIZE(points_seq)) {
        PyErr_SetString(PyExc_ValueError, "scalars and points must have equal length");
        Py_DECREF(scalars_seq);
        Py_DECREF(points_seq);
        return NULL;
    }
    if (n <= 0) {
        PyErr_SetString(PyExc_ValueError, "empty input lists");
        Py_DECREF(scalars_seq);
        Py_DECREF(points_seq);
        return NULL;
    }

    /* allocate buffers for reduced stuff */
    size_t buf_sz = (size_t)n * 32;
    unsigned char *scalars_buf = (unsigned char *)malloc(buf_sz);
    unsigned char *points_buf  = (unsigned char *)malloc(buf_sz);
    if (!scalars_buf || !points_buf) {
        PyErr_NoMemory();
        free(scalars_buf);
        free(points_buf);
        Py_DECREF(scalars_seq);
        Py_DECREF(points_seq);
        return NULL;
    }

    /* pre-process while holding GIL */
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject *py_sc = PySequence_Fast_GET_ITEM(scalars_seq, i); /* borrowed */
        PyObject *py_pt = PySequence_Fast_GET_ITEM(points_seq, i);  /* borrowed */

        if (!PyLong_Check(py_sc)) {
            PyErr_SetString(PyExc_TypeError, "each scalar must be a python int");
            goto fail_preprocess;
        }
        if (!PyBytes_Check(py_pt) || PyBytes_Size(py_pt) != 32) {
            PyErr_SetString(PyExc_TypeError, "each point must be 32-byte bytes (ristretto encoding)");
            goto fail_preprocess;
        }

        /* scalar -> 32-byte reduced */
        unsigned char tmp_reduced[32];
        if (py_long_to_reduced32(py_sc, tmp_reduced) != 0) {
            PyErr_SetString(PyExc_ValueError, "failed to convert scalar to 32-byte little-endian scalar");
            goto fail_preprocess;
        }
        memcpy(scalars_buf + (size_t)i * 32, tmp_reduced, 32);

        /* copy point bytes into contiguous buffer */
        const unsigned char *ptdata = (const unsigned char *)PyBytes_AS_STRING(py_pt);
        memcpy(points_buf + (size_t)i * 32, ptdata, 32);
    }

    /* decref sequences */
    Py_DECREF(scalars_seq);
    Py_DECREF(points_seq);
    scalars_seq = points_seq = NULL;

    /* prepare accumulator */
    unsigned char acc[32];
    memset(acc, 0, 32);

    unsigned char tmp_point_mul[32];

    /* release GIL */
    Py_BEGIN_ALLOW_THREADS;
    for (Py_ssize_t i = 0; i < n; ++i) {
        const unsigned char *scalar_ptr = scalars_buf + (size_t)i * 32;
        const unsigned char *point_ptr  = points_buf + (size_t)i * 32;

        int is_zero = 1;
        for (int k = 0; k < 32; ++k) {
            if (scalar_ptr[k] != 0) { is_zero = 0; break; }
        }
        if (is_zero) {
            continue;
        }

        /* scalar * point */
        if (crypto_scalarmult_ristretto255(tmp_point_mul, scalar_ptr, point_ptr) != 0) {
            /* set error flag */
            memset(acc, 0xFF, 32);
            break;
        }

        /* acc = acc + tmp_point_mul */
        crypto_core_ristretto255_add(acc, acc, tmp_point_mul);
    }
    Py_END_ALLOW_THREADS;

    /* sentinel failure */
    int failed = 0;
    for (int k = 0; k < 32; ++k) {
        if (acc[k] != 0xFF) { failed = 0; break; }
        failed = 1;
    }
    if (failed) {
        free(scalars_buf);
        free(points_buf);
        PyErr_SetString(PyExc_RuntimeError, "crypto_scalarmult_ristretto255 failed (invalid point?)");
        return NULL;
    }

    /* return py bytes */
    PyObject *ret = PyBytes_FromStringAndSize((const char *)acc, 32);

    free(scalars_buf);
    free(points_buf);
    return ret;

fail_preprocess:
    /* decref, cleanup */
    free(scalars_buf);
    free(points_buf);
    Py_DECREF(scalars_seq);
    Py_DECREF(points_seq);
    return NULL;
}

/* method table */
static PyMethodDef Methods[] = {
    {"msm", msm, METH_VARARGS, "msm(scalars: sequence[int], points: sequence[bytes]) -> bytes (32-byte ristretto point)"},
    {NULL, NULL, 0, NULL}
};

/* module definition */
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "msm",
    "Optimized Naive MSM C extension for Ristretto255 using libsodium",
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_msm(void) {
    if (sodium_init() < 0) {
        PyErr_SetString(PyExc_RuntimeError, "libsodium initialization failed");
        return NULL;
    }
    return PyModule_Create(&moduledef);
}
