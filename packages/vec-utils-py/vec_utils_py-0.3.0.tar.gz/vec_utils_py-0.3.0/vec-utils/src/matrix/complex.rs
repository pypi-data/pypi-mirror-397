use core::ops::Mul;

use matrixmultiply::zgemm;

use crate::complex::Complex;
#[doc(inline)]
use crate::matrix::generic::GMatrix;

/// A 2d complex matrix of width R and height C
pub type CMatrix<const R: usize, const C: usize> = GMatrix<R, C, Complex>;

/// An alias for 2x2 matracies
pub type CMatrix2x2 = CMatrix<2, 2>;
/// An alias for 3x3 matracies
pub type CMatrix3x3 = CMatrix<3, 3>;

impl<const R: usize, const C: usize> CMatrix<R, C> where [Complex; R * C]: Sized {}

impl<const R: usize, const C: usize, const U: usize> Mul<CMatrix<U, C>> for CMatrix<R, U>
where
    [Complex; R * C]: Sized,
    [Complex; R * U]: Sized,
    [Complex; U * C]: Sized
{
    type Output = CMatrix<R, C>;

    fn mul(self, rhs: CMatrix<U, C>) -> Self::Output {
        let mut result = CMatrix::<R, C>::zeros();
        // Safety: [Complex; R * C] and [[f64; 2]; R * C] have the exact same memory layout. zgemm
        // is an unsafe function.
        unsafe {
            let lhs_ptr = (&raw const self.values).cast::<[f64; 2]>();
            let rhs_ptr = (&raw const rhs.values).cast::<[f64; 2]>();
            let result_ptr = (&raw mut result.values).cast::<[f64; 2]>();
            zgemm(
                matrixmultiply::CGemmOption::Standard,
                matrixmultiply::CGemmOption::Standard,
                R,
                U,
                C,
                [1.0, 0.0],
                lhs_ptr,
                U.cast_signed(),
                1,
                rhs_ptr,
                C.cast_signed(),
                1,
                [0.0; 2],
                result_ptr,
                C.cast_signed(),
                1
            );
        }
        result
    }
}

#[cfg(test)]
mod tests {
    use pretty_assertions::assert_eq;

    use super::*;

    #[test]
    fn test_mul() {
        let a = CMatrix2x2::from_nested_arr([
            [Complex::new(1.0, 0.0), Complex::new(0.0, 1.0)],
            [Complex::new(0.0, 0.0), Complex::new(2.0, 0.0)]
        ]);

        let b = CMatrix2x2::from_nested_arr([
            [Complex::new(0.0, 1.0), Complex::new(1.0, 0.0)],
            [Complex::new(1.0, 0.0), Complex::new(0.0, 1.0)]
        ]);

        let correct = CMatrix2x2::from_nested_arr([
            [Complex::new(0.0, 2.0), Complex::new(0.0, 0.0)],
            [Complex::new(2.0, 0.0), Complex::new(0.0, 2.0)]
        ]);

        let result = a * b;

        assert_eq!(result, correct);
        let a = CMatrix3x3::from_nested_arr([
            [
                Complex::new(1.0, 2.0),
                Complex::new(3.0, 4.0),
                Complex::new(5.0, 6.0)
            ],
            [
                Complex::new(7.0, 8.0),
                Complex::new(9.0, 0.0),
                Complex::new(1.0, 1.0)
            ],
            [
                Complex::new(0.0, 0.0),
                Complex::new(2.0, 2.0),
                Complex::new(3.0, 3.0)
            ]
        ]);

        let zero_mat = CMatrix3x3::zeros();
        let result = a * zero_mat;
        assert_eq!(result, zero_mat);
    }
}
