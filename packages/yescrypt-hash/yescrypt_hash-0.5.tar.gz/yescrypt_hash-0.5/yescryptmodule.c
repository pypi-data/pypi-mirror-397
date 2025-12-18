#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "yescrypthash.h"

static PyObject *yescrypt_getpowhash(PyObject *self, PyObject *args)
{
    char *output;
    PyObject *value;
#if PY_MAJOR_VERSION >= 3
    PyBytesObject *input;
#else
    PyStringObject *input;
#endif
    if (!PyArg_ParseTuple(args, "S", &input))
        return NULL;
    Py_INCREF(input);
    output = PyMem_Malloc(32);

#if PY_MAJOR_VERSION >= 3
    yescrypt_hash((char *)PyBytes_AsString((PyObject*) input), output);
#else
    yescrypt_hash((char *)PyString_AsString((PyObject*) input), output);
#endif
    Py_DECREF(input);
#if PY_MAJOR_VERSION >= 3
    value = Py_BuildValue("y#", output, 32);
#else
    value = Py_BuildValue("s#", output, 32);
#endif
    PyMem_Free(output);
    return value;
}

static PyMethodDef YescryptMethods[] = {
    { "getPoWHash", yescrypt_getpowhash, METH_VARARGS, "Returns the proof of work hash using yescrypt hash" },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef YescryptModule = {
    PyModuleDef_HEAD_INIT,
    "yescrypt_hash",
    "...",
    -1,
    YescryptMethods
};

PyMODINIT_FUNC PyInit_yescrypt_hash(void) {
    return PyModule_Create(&YescryptModule);
}

#else

PyMODINIT_FUNC inityescrypt_hash(void) {
    (void) Py_InitModule("yescrypt_hash", YescryptMethods);
}
#endif
