#ifndef GAUSS_SEIDEL_H
#define GAUSS_SEIDEL_H

#include "types.h"
#include "mangling.h"

/* =========================
 * FORTRAN API DECLARATIONS
 * ========================= */

fortran API_cgssv(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                  INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_dgssv(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                  INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);

fortran API_sgssv(INTEGER* N, REAL* A, REAL* B, REAL* X,
                  INTEGER* MAX_ITER, REAL* TOL, REAL* OMEGA, INTEGER* STATUS);

fortran API_zgssv(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                  INTEGER* MAX_ITER, DOUBLE* TOL, DOUBLE* OMEGA, INTEGER* STATUS);


#ifdef __cplusplus

    /* ==============
     * C++ INTERFACE
     * ============== */

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, REAL* A, REAL* B, REAL* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_sgssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, DOUBLE* A, DOUBLE* B, DOUBLE* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_dgssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, COMPLEX* A, COMPLEX* B, COMPLEX* X,
                            INTEGER* MAX_ITER, REAL* TOL, INTEGER* STATUS, REAL OMEGA = 1.0) {
        API_cgssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

    SUBROUTINE GAUSS_SEIDEL(INTEGER* N, DOUBLE_COMPLEX* A, DOUBLE_COMPLEX* B, DOUBLE_COMPLEX* X,
                            INTEGER* MAX_ITER, DOUBLE* TOL, INTEGER* STATUS, DOUBLE OMEGA = 1.0) {
        API_zgssv(N, A, B, X, MAX_ITER, TOL, &OMEGA, STATUS);
    }

#else  // C-only fallback

    /* ===========
     * C INTERFACE
     * ============ */

    #define GAUSS_SEIDEL(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)  \
        _Generic((A),                                                \
            REAL*:            API_sgssv,                             \
            DOUBLE*:          API_dgssv,                             \
            COMPLEX*:         API_cgssv,                             \
            DOUBLE_COMPLEX*:  API_zgssv                              \
        )(N, A, B, X, MAX_ITER, TOL, OMEGA, STATUS)

#endif

#endif
