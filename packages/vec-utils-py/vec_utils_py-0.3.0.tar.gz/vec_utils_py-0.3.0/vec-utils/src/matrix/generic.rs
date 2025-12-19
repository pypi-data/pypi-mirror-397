use core::fmt::Debug;
use core::ops::{Add, Div, Index, IndexMut, Mul, Sub};
#[cfg(feature = "std")]
use std::vec::Vec;

use crate::matrix::traits::{Oneable, Signed, Zeroable};

/// A generic 2d matrix of width R and height C
// TODO: I would like to add a generic is row major switch
#[derive(Debug, Copy, Clone, PartialEq)]
pub struct GMatrix<const R: usize, const C: usize, T>
where
    [T; R * C]: Sized
{
    pub(crate) values: [T; R * C]
}

/// An alias for 2x2 matracies
pub type GMatrix2x2<T> = GMatrix<2, 2, T>;
/// An alias for 3x3 matracies
pub type GMatrix3x3<T> = GMatrix<3, 3, T>;

impl<const R: usize, const C: usize, T> GMatrix<R, C, T>
where
    [T; R * C]: Sized,
    T: Debug
        + Oneable
        + Zeroable
        + Copy
        + Clone
        + PartialEq
        + Signed
        + PartialOrd
        + Mul<Output = T>
        + Div<Output = T>
        + Sub<Output = T>
        + Add<Output = T>
{
    const IS_2X2: bool = R == 2 && C == 2;
    const IS_3X3: bool = R == 3 && C == 3;
    const IS_ONE_DIMM: bool = R == 1 || C == 1;
    const IS_SQUARE: bool = R == C;

    /// Create a matrix from nested vectors.
    /// # Panics
    /// A misshapen vector, i.e. one that's not of length C or that doesnt contain vectors of exclusively length R
    #[cfg(feature = "std")]
    pub fn from_nested_vec(values: Vec<Vec<T>>) -> Self {
        let flattened: Vec<T> = values.into_iter().flatten().collect();
        let values: [T; R * C] = flattened
            .try_into()
            .expect("Input dimensions do not match Matrix size R * C");
        Self { values }
    }

    /// Create a matrix from nested arrays.
    pub fn from_nested_arr(values: [[T; C]; R]) -> Self {
        // Safety: [[T; C]; R] and [T; R * C] have the exact same memory layout
        let flat_values = unsafe {
            let ptr = (&raw const values).cast::<[T; R * C]>();
            core::ptr::read(ptr)
        };

        let _ = values;

        Self {
            values: flat_values
        }
    }

    /// Convert a matrix into nested arrays.
    pub fn to_nested_arr(&self) -> [[T; C]; R] {
        // Safety: [[T; C]; R] and [T; R * C] have the exact same memory layout
        let nested_values = unsafe {
            let ptr = (&raw const self.values).cast::<[[T; C]; R]>();
            core::ptr::read(ptr)
        };

        let _ = self.values;

        nested_values
    }

    /// Create a matrix filled with zeros
    pub fn zeros() -> Self {
        Self {
            values: [T::zero(); R * C]
        }
    }

    /// Create a matrix filled with ones
    pub fn ones() -> Self {
        Self {
            values: [T::one(); R * C]
        }
    }

    /// Determines if the matrix is square
    pub fn is_square() -> bool {
        Self::IS_SQUARE
    }

    /// Counts the number of nonzero values
    pub fn count_nonzero(&self) -> usize {
        self.values
            .iter()
            .fold(0, |acc, i| if i.is_zero() { acc } else { acc + 1 })
    }

    /// Returns the diagonal elements
    #[cfg(feature = "std")]
    pub fn diagonals(&self) -> Vec<T> {
        let min_dimm = R.min(C);
        (0..min_dimm).map(|i| self.values[i + i * C]).collect()
    }

    /// Checks if the matrix is upper triangluar
    /// This does not check if its strictly upper triangluar
    pub fn is_upper_triangular(&self) -> bool {
        for row in 1..R {
            for col in 0..row.min(C) {
                if !self.values[row * C + col].is_zero() {
                    return false;
                }
            }
        }
        true
    }

    /// Checks if the matrix is lower triangluar
    /// This does not check if its strictly lower triangluar
    pub fn is_lower_triangular(&self) -> bool {
        for row in 0..R.min(C) {
            for col in (row + 1)..C {
                if !self.values[row * C + col].is_zero() {
                    return false;
                }
            }
        }
        true
    }

    /// Checks if the matrix is a diagonal matrix
    pub fn is_diagonal(&self) -> bool {
        for row in 0..R {
            for col in 0..row.min(C) {
                if !self.values[row * C + col].is_zero() {
                    return false;
                }
            }
            if row + 1 < C {
                for col in (row + 1)..C {
                    if !self.values[row * C + col].is_zero() {
                        return false;
                    }
                }
            }
        }
        true
    }

    /// Iterates over the matrix with enumerated position values
    pub fn iter_indexed(&self) -> impl Iterator<Item = ((usize, usize), &T)> {
        self.values.iter().enumerate().map(|(idx, val)| {
            let r = idx / C;
            let c = idx % C;
            ((r, c), val)
        })
    }

    /// Iterates over the matrix
    pub fn iter(&self) -> impl Iterator<Item = &T> {
        self.values.iter()
    }

    /// Mutably iterates over the matrix
    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut T> {
        self.values.iter_mut()
    }

    /// Mutably iterates over the matrix with enumerated position values
    pub fn iter_indexed_mut(&mut self) -> impl Iterator<Item = ((usize, usize), &mut T)> {
        self.values.iter_mut().enumerate().map(|(idx, val)| {
            let r = idx / C;
            let c = idx % C;
            ((r, c), val)
        })
    }

    /// Calculates the determinant of the matrix
    /// # Panics
    /// If the matrix is not square
    pub fn determinant(&self) -> T {
        if Self::IS_2X2 {
            self.values[0] * self.values[3] - self.values[1] * self.values[2]
        } else if Self::IS_3X3 {
            self.values[0] * self.values[4] * self.values[8]
                + self.values[1] * self.values[5] * self.values[6]
                + self.values[2] * self.values[3] * self.values[7]
                - self.values[2] * self.values[4] * self.values[6]
                - self.values[1] * self.values[3] * self.values[8]
                - self.values[0] * self.values[5] * self.values[7]
        } else if Self::IS_SQUARE {
            let mut lu = self.values;
            let mut sign = T::one();

            for i in 0..R {
                let mut pivot = i;
                for j in (i + 1)..R {
                    if lu[j * C + i].abs() > lu[pivot * C + i].abs() {
                        pivot = j;
                    }
                }

                if lu[pivot * C + i].is_zero() {
                    return T::zero();
                }

                if pivot != i {
                    for k in 0..C {
                        lu.swap(i * C + k, pivot * C + k);
                    }
                    sign.flip();
                }

                for j in (i + 1)..R {
                    let factor = lu[j * C + i] / lu[i * C + i];
                    for k in (i + 1)..C {
                        let val = lu[i * C + k];
                        lu[j * C + k] = lu[j * C + k] - factor * val;
                    }
                }
            }

            let mut det = sign;
            for i in 0..R {
                det = det * lu[i * C + i];
            }

            det
        } else {
            panic!("Cannot take the determinant of a non square matrix");
        }
    }

    /// Returns the minor submatrix by removing the provided row and column
    /// # Panics
    /// Will panic if the generic ROUT and COUT are not 1 less than R and C
    pub fn get_minor_submatrix<const ROUT: usize, const COUT: usize>(
        &self,
        row_to_skip: usize,
        col_to_skip: usize
    ) -> GMatrix<ROUT, COUT, T>
    where
        [T; ROUT * COUT]: Sized
    {
        assert_eq!(ROUT, R - 1, "Wrong sized generics. Output rows must be R-1");
        assert_eq!(
            COUT,
            C - 1,
            "Wrong sized generics. Output columns must be C-1"
        );

        let mut sub_values = [T::zero(); ROUT * COUT];
        let mut sub_idx = 0;

        for r in 0..R {
            if r == row_to_skip {
                continue;
            }
            for c in 0..C {
                if c == col_to_skip {
                    continue;
                }
                sub_values[sub_idx] = self.values[r * C + c];
                sub_idx += 1;
            }
        }

        GMatrix { values: sub_values }
    }

    /// Calculates the cofactor of the matrix at the provided row and column
    pub fn cofactor(&self, row: usize, col: usize) -> T
    where
        [T; (R - 1) * (C - 1)]: Sized
    {
        let sub = self.get_minor_submatrix::<{ R - 1 }, { C - 1 }>(row, col);
        let minor_det = sub.determinant();

        if (row + col).is_multiple_of(2) {
            minor_det
        } else {
            T::zero() - minor_det
        }
    }

    /// Returns the full matrix of cofactors
    pub fn cofactor_matrix(&self) -> GMatrix<R, C, T>
    where
        [T; (R - 1) * (C - 1)]: Sized
    {
        let mut cofactors = [T::zero(); R * C];
        for r in 0..R {
            for c in 0..C {
                cofactors[r * C + c] = self.cofactor(r, c);
            }
        }
        GMatrix { values: cofactors }
    }

    /// Transposes the matrix.
    /// For matriacies with a dimension of 1 this is zerocopy.
    /// Otherwise it has to touch every value.
    pub fn transpose(&self) -> GMatrix<C, R, T>
    where
        [T; C * R]: Sized
    {
        if Self::IS_ONE_DIMM {
            // Safety: Both GMatrix<R, C, T> and GMatrix<C, R, T> have the same size and
            // both represent a contiguous strip of memory.
            // transmute_copy is used to move the bits into the new type.
            unsafe {
                let result = core::mem::transmute_copy::<Self, GMatrix<C, R, T>>(self);
                let _ = self;
                result
            }
        } else {
            // TODO: implement blocking for bigger matracies
            let mut output = [T::zero(); C * R];
            for row in 0..R {
                for col in 0..C {
                    output[col * R + row] = self.values[row * C + col];
                }
            }
            GMatrix::<C, R, T> { values: output }
        }
    }

    /// Calculate the adjoint of a 3x3 matrix
    /// i.e. the transpose of the cofactor matrix
    pub fn adjoint(&self) -> GMatrix<C, R, T>
    where
        [T; (R - 1) * (C - 1)]: Sized,
        [T; C * R]: Sized
    {
        self.cofactor_matrix().transpose()
    }
}

impl<const R: usize, const C: usize, T> Index<[usize; 2]> for GMatrix<R, C, T>
where
    [T; R * C]: Sized
{
    type Output = T;

    fn index(&self, idx: [usize; 2]) -> &Self::Output {
        let [row, col] = idx;
        assert!(
            row < R && col < C,
            "Index [{row}, {col}] is out of bounds for matrix of shape [{R}, {C}]"
        );
        &self.values[row * C + col]
    }
}

impl<const R: usize, const C: usize, T> IndexMut<[usize; 2]> for GMatrix<R, C, T>
where
    [T; R * C]: Sized
{
    fn index_mut(&mut self, idx: [usize; 2]) -> &mut Self::Output {
        let [row, col] = idx;
        assert!(
            row < R && col < C,
            "Index [{row}, {col}] is out of bounds for matrix of shape [{R}, {C}]"
        );
        &mut self.values[row * C + col]
    }
}

#[cfg(test)]
mod tests {
    use assert_float_eq::assert_f64_near;
    use pretty_assertions::assert_eq;

    use super::*;
    use crate::complex::Complex;

    #[test]
    fn test_constructors_f64() {
        let zero = GMatrix2x2::<f64>::zeros();
        let one = GMatrix2x2::<f64>::ones();

        for i in zero.iter() {
            assert_f64_near!(*i, 0.0);
        }
        for i in one.iter() {
            assert_f64_near!(*i, 1.0);
        }

        let arr = GMatrix2x2::from_nested_arr([[1.0, 2.0], [3.0, 4.0]]);
        assert_f64_near!(arr[[0, 0]], 1.0);
        assert_f64_near!(arr[[1, 1]], 4.0);
    }

    #[test]
    fn test_constructors_complex() {
        let c1 = Complex {
            real: 1.0,
            imaginary: 2.0
        };
        let c2 = Complex {
            real: 3.0,
            imaginary: 4.0
        };
        let mat = GMatrix::<1, 2, Complex>::from_nested_arr([[c1, c2]]);

        assert_eq!(mat[[0, 0]], c1);
        assert_eq!(mat[[0, 1]], c2);
    }

    #[test]
    fn test_shape_properties() {
        assert!(GMatrix2x2::<f64>::is_square());
        assert!(!GMatrix::<2, 3, f64>::is_square());

        let mut mat = GMatrix2x2::<f64>::zeros();
        mat[[0, 0]] = 1.0;
        mat[[1, 1]] = 1.0;
        assert_eq!(mat.count_nonzero(), 2);
    }

    #[test]
    fn test_triangular_checks() {
        let ut = GMatrix2x2::<f64>::from_nested_arr([[1.0, 2.0], [0.0, 3.0]]);
        assert!(ut.is_upper_triangular());
        assert!(!ut.is_lower_triangular());

        let lt = GMatrix2x2::<f64>::from_nested_arr([[1.0, 0.0], [2.0, 3.0]]);
        assert!(lt.is_lower_triangular());
        assert!(!lt.is_upper_triangular());

        let diag = GMatrix2x2::<f64>::from_nested_arr([[1.0, 0.0], [0.0, 3.0]]);
        assert!(diag.is_diagonal());
    }

    #[test]
    fn test_iterators() {
        let mut mat = GMatrix2x2::<f64>::from_nested_arr([[1.0, 2.0], [3.0, 4.0]]);

        let indexed: Vec<((usize, usize), f64)> =
            mat.iter_indexed().map(|(pos, &val)| (pos, val)).collect();
        assert_eq!(indexed[1], ((0, 1), 2.0));

        // Mutable iteration
        for ((r, c), val) in mat.iter_indexed_mut() {
            if r == c {
                *val = 0.0;
            }
        }
        assert_f64_near!(mat[[0, 0]], 0.0);
        assert_f64_near!(mat[[1, 1]], 0.0);
    }

    #[test]
    fn test_transpose() {
        // Test Vector (Zero-Copy path)
        let vec = GMatrix::<1, 3, f64>::from_nested_arr([[1.0, 2.0, 3.0]]);
        let vec_t = vec.transpose();
        assert_f64_near!(vec_t[[0, 0]], 1.0);
        assert_f64_near!(vec_t[[2, 0]], 3.0);

        // Test Matrix (Standard path)
        let mat = GMatrix2x2::<f64>::from_nested_arr([[1.0, 2.0], [3.0, 4.0]]);
        let mat_t = mat.transpose();
        assert_f64_near!(mat_t[[0, 1]], 3.0);
        assert_f64_near!(mat_t[[1, 0]], 2.0);
    }

    #[test]
    #[should_panic(expected = "out of bounds")]
    fn test_index_out_of_bounds() {
        let mat = GMatrix2x2::<f64>::zeros();
        let _ = mat[[2, 0]];
    }

    #[test]
    #[cfg(feature = "std")]
    fn test_diagonals() {
        let mat =
            GMatrix3x3::<f64>::from_nested_arr([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]]);
        assert_eq!(mat.diagonals(), vec![1.0, 2.0, 3.0]);
    }

    #[test]
    fn test_determinant_2x2() {
        let m = GMatrix::<2, 2, f64> {
            values: [1.0, 2.0, 3.0, 4.0]
        };
        assert_f64_near!(m.determinant(), -2.0);
    }

    #[test]
    fn test_determinant_3x3() {
        let m = GMatrix::<3, 3, f64> {
            values: [6.0, 1.0, 1.0, 4.0, -2.0, 5.0, 2.0, 8.0, 7.0]
        };
        assert_f64_near!(m.determinant(), -306.0);
    }

    #[test]
    fn test_determinant_4x4_lu() {
        let m = GMatrix::<4, 4, f64> {
            values: [
                1.0, 3.0, 5.0, 9.0, 1.0, 3.0, 1.0, 7.0, 4.0, 3.0, 9.0, 7.0, 5.0, 2.0, 0.0, 9.0
            ]
        };
        assert_f64_near!(m.determinant(), -376.0);
    }

    #[test]
    fn test_determinant_singular() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        };
        assert_f64_near!(m.determinant(), 0.0);
    }

    #[test]
    fn test_determinant_identity() {
        let m = GMatrix::<4, 4, f64> {
            values: [
                1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0
            ]
        };
        assert_f64_near!(m.determinant(), 1.0);
    }

    #[test]
    #[should_panic(expected = "Cannot take the determinant of a non square matrix")]
    fn test_determinant_non_square_panic() {
        let m = GMatrix::<2, 3, f64> {
            values: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        };
        let _ = m.determinant();
    }

    #[test]
    fn test_minor_submatrix_extraction() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        };

        let sub = m.get_minor_submatrix::<2, 2>(0, 1);
        let expected = [4.0, 6.0, 7.0, 9.0];

        for (i, j) in sub.values.into_iter().zip(expected.into_iter()) {
            assert_f64_near!(i, j);
        }
    }

    #[test]
    fn test_cofactor_values() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 3.0, 2.0, 4.0, 5.0, 0.0, 2.0, 1.0, 2.0]
        };

        assert_f64_near!(m.cofactor(1, 1), -2.0);
        assert_f64_near!(m.cofactor(0, 1), -8.0);
    }

    #[test]
    fn test_full_cofactor_matrix() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 2.0, 3.0, 0.0, 4.0, 5.0, 1.0, 0.0, 6.0]
        };

        let cofactors = m.cofactor_matrix();
        let expected = [24.0, 5.0, -4.0, -12.0, 3.0, 2.0, -2.0, -5.0, 4.0];

        for (i, j) in cofactors.values.into_iter().zip(expected.into_iter()) {
            assert_f64_near!(i, j);
        }
    }

    #[test]
    fn test_cofactor_determinant_consistency() {
        let m = GMatrix::<3, 3, f64> {
            values: [3.0, 5.0, 0.0, 2.0, -1.0, 4.0, 6.0, 0.0, 2.0]
        };

        let det_direct = m.determinant();

        let det_expansion = m.values[0] * m.cofactor(0, 0)
            + m.values[1] * m.cofactor(0, 1)
            + m.values[2] * m.cofactor(0, 2);

        assert_f64_near!(det_direct, det_expansion);
    }

    #[test]
    #[should_panic(expected = "Wrong sized generics")]
    fn test_minor_wrong_dimensions_panic() {
        let m = GMatrix::<3, 3, f64> { values: [0.0; 9] };
        let _ = m.get_minor_submatrix::<3, 3>(0, 0);
    }

    #[test]
    fn test_adjoint_2x2() {
        let m = GMatrix::<2, 2, f64> {
            values: [1.0, 2.0, 3.0, 4.0]
        };
        let adj = m.adjoint();
        let expected = [4.0, -2.0, -3.0, 1.0];

        for (i, j) in adj.values.into_iter().zip(expected.into_iter()) {
            assert_f64_near!(i, j);
        }
    }

    #[test]
    fn test_adjoint_3x3() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 2.0, 3.0, 0.0, 1.0, 4.0, 5.0, 6.0, 0.0]
        };

        let adj = m.adjoint();
        let expected = [-24.0, 18.0, 5.0, 20.0, -15.0, -4.0, -5.0, 4.0, 1.0];

        for (i, j) in adj.values.into_iter().zip(expected.into_iter()) {
            assert_f64_near!(i, j);
        }
    }

    #[test]
    fn test_adjoint_inverse_relationship() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 2.0, 3.0, 0.0, 4.0, 5.0, 1.0, 0.0, 6.0]
        };

        let det = m.determinant();
        let adj = m.adjoint();

        let row0_col0 = (m.values[0] * adj.values[0]
            + m.values[1] * adj.values[3]
            + m.values[2] * adj.values[6]);

        assert_f64_near!(row0_col0, det);
    }

    #[test]
    fn test_adjoint_identity() {
        let m = GMatrix::<3, 3, f64> {
            values: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        };
        let adj = m.adjoint();
        let expected = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0];

        for (i, j) in adj.values.into_iter().zip(expected.into_iter()) {
            assert_f64_near!(i, j);
        }
    }
}
