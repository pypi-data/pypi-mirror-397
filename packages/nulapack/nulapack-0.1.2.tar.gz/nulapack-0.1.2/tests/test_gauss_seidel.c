#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <complex.h>
#include "gauss-seidel.h"
#include "utils.h"

void TEST_CASE_FLOAT32() {
    const char* test_name = "SGSSV - SINGLE PRECISION GAUSS-SEIDEL SOLVER [FLOAT32]";
    PRINT_INFO(test_name);

    int N = 4;
    float A[16] = {
        10.0f, -1.0f, 2.0f, 0.0f,
        -1.0f, 11.0f, -1.0f, 3.0f,
        2.0f, -1.0f, 10.0f, -1.0f,
        0.0f, 3.0f, -1.0f, 8.0f
    };
    float B[4] = {6.0f, 25.0f, -11.0f, 15.0f};
    float X[4] = {0};
    int max_iter = 1000;
    float tol = 1e-4f;
    float omega = 1.0f;
    int status;

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &omega, &status);

    for (int i = 0; i < N; i++) printf("X[%d] = %.6f\n", i, X[i]);

    TEST_ASSERT(status == 0, "status should be 0");
    TEST_ASSERT(float_within_abs(X[0], 1.0f, 1e-5f), "X[0] should be ~1.0");
    TEST_ASSERT(float_within_abs(X[1], 2.0f, 1e-5f), "X[1] should be ~2.0");
    TEST_ASSERT(float_within_abs(X[2], -1.0f, 1e-5f), "X[2] should be ~-1.0");
    TEST_ASSERT(float_within_abs(X[3], 1.0f, 1e-5f), "X[3] should be ~1.0");
    test_passed++;
}

void TEST_CASE_FLOAT64() {
    const char* test_name = "DGSSV - DOUBLE PRECISION GAUSS-SEIDEL SOLVER [FLOAT64]";
    PRINT_INFO(test_name);

    int N = 4;
    double A[16] = {
        10.0, -1.0, 2.0, 0.0,
        -1.0, 11.0, -1.0, 3.0,
        2.0, -1.0, 10.0, -1.0,
        0.0, 3.0, -1.0, 8.0
    };
    double B[4] = {6.0, 25.0, -11.0, 15.0};
    double X[4] = {0};
    int max_iter = 1000;
    double tol = 1e-10;
    double omega = 1.0;
    int status;

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &omega, &status);

    for (int i = 0; i < N; i++) printf("X[%d] = %.12lf\n", i, X[i]);

    TEST_ASSERT(status == 0, "status should be 0");
    TEST_ASSERT(double_within_abs(X[0], 1.0, 1e-10), "X[0] should be ~1.0");
    TEST_ASSERT(double_within_abs(X[1], 2.0, 1e-10), "X[1] should be ~2.0");
    TEST_ASSERT(double_within_abs(X[2], -1.0, 1e-10), "X[2] should be ~-1.0");
    TEST_ASSERT(double_within_abs(X[3], 1.0, 1e-10), "X[3] should be ~1.0");
    test_passed++;
}

void TEST_CASE_COMPLEX64() {
    const char* test_name = "CGSSV - COMPLEX FLOAT GAUSS-SEIDEL SOLVER [COMPLEX64]";
    PRINT_INFO(test_name);

    int N = 4;
    float _Complex A[16] = {
        10.0f + 1.0f*I, -1.0f + 0.0f*I, 2.0f + 0.0f*I, 0.0f + 0.0f*I,
        -1.0f + 0.0f*I, 11.0f + 1.0f*I, -1.0f + 0.0f*I, 3.0f + 0.0f*I,
        2.0f + 0.0f*I, -1.0f + 0.0f*I, 10.0f + 1.0f*I, -1.0f + 0.0f*I,
        0.0f + 0.0f*I, 3.0f + 0.0f*I, -1.0f + 0.0f*I, 8.0f + 1.0f*I
    };
    float _Complex B[4] = {
        6.0f + 1.0f*I, 25.0f + 2.0f*I, -11.0f + 1.0f*I, 15.0f - 1.0f*I
    };
    float _Complex X[4] = {0};
    int max_iter = 1000;
    float tol = 1e-4f;
    float omega = 1.0f;
    int status;

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &omega, &status);

    for (int i = 0; i < N; i++) {
        printf("X[%d] = (%.6f, %.6f)\n", i, crealf(X[i]), cimagf(X[i]));
    }

    TEST_ASSERT(status == 0, "status should be 0");
    TEST_ASSERT(complex_float_within_abs(X[0], 0.995412f - 0.028752f*I, 1e-5f), "X[0] should be ~(0.995412, -0.028752)");
    TEST_ASSERT(complex_float_within_abs(X[1], 2.018524f + 0.081610f*I, 1e-5f), "X[1] should be ~(2.018524, 0.081610)");
    TEST_ASSERT(complex_float_within_abs(X[2], -0.982175f + 0.186858f*I, 1e-5f), "X[2] should be ~(-0.982175, 0.186858)");
    TEST_ASSERT(complex_float_within_abs(X[3], 0.963693f - 0.252708f*I, 1e-5f), "X[3] should be ~(0.963693, -0.252708)");
    test_passed++;
}

void TEST_CASE_COMPLEX128() {
    const char* test_name = "ZGSSV - COMPLEX DOUBLE GAUSS-SEIDEL SOLVER [COMPLEX128]";
    PRINT_INFO(test_name);

    int N = 4;
    double _Complex A[16] = {
        10.0 + 1.0*I, -1.0 + 0.0*I, 2.0 + 0.0*I, 0.0 + 0.0*I,
        -1.0 + 0.0*I, 11.0 + 1.0*I, -1.0 + 0.0*I, 3.0 + 0.0*I,
        2.0 + 0.0*I, -1.0 + 0.0*I, 10.0 + 1.0*I, -1.0 + 0.0*I,
        0.0 + 0.0*I, 3.0 + 0.0*I, -1.0 + 0.0*I, 8.0 + 1.0*I
    };
    double _Complex B[4] = {
        6.0 + 1.0*I, 25.0 + 2.0*I, -11.0 + 1.0*I, 15.0 - 1.0*I
    };
    double _Complex X[4] = {0};
    int max_iter = 1000;
    double tol = 1e-12;
    double omega = 1.0;
    int status;

    GAUSS_SEIDEL(&N, A, B, X, &max_iter, &tol, &omega, &status);

    for (int i = 0; i < N; i++) {
        printf("X[%d] = (%.12lf, %.12lf)\n", i, creal(X[i]), cimag(X[i]));
    }

    TEST_ASSERT(status == 0, "status should be 0");
    TEST_ASSERT(complex_double_within_abs(X[0], 0.995412230296 - 0.028751867347*I, 1e-11), "X[0] should be ~(0.995412230296, -0.028751867347)");
    TEST_ASSERT(complex_double_within_abs(X[1], 2.018524356148 + 0.081609612259*I, 1e-11), "X[1] should be ~(2.018524356148, 0.081609612259)");
    TEST_ASSERT(complex_double_within_abs(X[2], -0.982174907078 + 0.186858027715*I, 1e-11), "X[2] should be ~(-0.982174907078, 0.186858027715)");
    TEST_ASSERT(complex_double_within_abs(X[3], 0.963693005950 - 0.252707976877*I, 1e-11), "X[3] should be ~(0.963693005950, -0.252707976877)");
    test_passed++;
}

int main() {
    TEST_CASE_FLOAT32();
    TEST_CASE_FLOAT64();
    TEST_CASE_COMPLEX64();
    TEST_CASE_COMPLEX128();

    printf("\n");
    printf("========================================\n");
    printf("SUMMARY\n");
    printf("========================================\n");
    printf("Total Tests: %d\n", test_count);
    printf("Passed: %d\n", test_passed);
    printf("Failed: %d\n", test_failed);
    printf("========================================\n");

    return test_failed == 0 ? 0 : 1;
}
