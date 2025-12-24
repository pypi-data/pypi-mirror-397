#ifndef TEST_UTILS_H
#define TEST_UTILS_H

int float_within_abs(float value, float expected, float tolerance) {
    return fabsf(value - expected) <= tolerance;
}

int double_within_abs(double value, double expected, double tolerance) {
    return fabs(value - expected) <= tolerance;
}

int complex_float_within_abs(float _Complex value, float _Complex expected, float tolerance) {
    float real_diff = fabsf(crealf(value) - crealf(expected));
    float imag_diff = fabsf(cimagf(value) - cimagf(expected));
    return (real_diff <= tolerance) && (imag_diff <= tolerance);
}

int complex_double_within_abs(double _Complex value, double _Complex expected, double tolerance) {
    double real_diff = fabs(creal(value) - creal(expected));
    double imag_diff = fabs(cimag(value) - cimag(expected));
    return (real_diff <= tolerance) && (imag_diff <= tolerance);
}

int test_count = 0;
int test_passed = 0;
int test_failed = 0;

void PRINT_INFO(const char* test_name) {
    test_count++;
    printf("\n");
    printf("--- TEST CASE ---\n");
    printf("%s\n", test_name);
    printf("\n");
}

void TEST_ASSERT(int condition, const char* message) {
    if (!condition) {
        printf("ASSERTION FAILED: %s\n", message);
        test_failed++;
    }
}

#endif