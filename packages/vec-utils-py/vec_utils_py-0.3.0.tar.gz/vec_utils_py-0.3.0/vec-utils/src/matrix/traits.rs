use crate::complex::Complex;

pub trait Zeroable {
    fn zero() -> Self;

    fn is_zero(&self) -> bool;
}

pub trait Oneable {
    fn one() -> Self;

    fn is_one(&self) -> bool;
}

pub trait Signed {
    fn abs(&self) -> Self;

    fn flip(&mut self);
}

impl Zeroable for f64 {
    fn is_zero(&self) -> bool {
        *self == 0.0
    }

    fn zero() -> Self {
        0.0
    }
}

impl Oneable for f64 {
    fn is_one(&self) -> bool {
        (self - 1.0).abs() < f64::EPSILON
    }

    fn one() -> Self {
        1.0
    }
}

impl Signed for f64 {
    fn abs(&self) -> Self {
        f64::abs(*self)
    }

    fn flip(&mut self) {
        *self *= -1.0;
    }
}

impl Zeroable for Complex {
    fn is_zero(&self) -> bool {
        self.real.abs() < f64::EPSILON && self.imaginary.abs() < f64::EPSILON
    }

    fn zero() -> Self {
        Self {
            real: 0.0,
            imaginary: 0.0
        }
    }
}

impl Oneable for Complex {
    fn is_one(&self) -> bool {
        (self.real - 1.0).abs() < f64::EPSILON && self.imaginary.abs() < f64::EPSILON
    }

    fn one() -> Self {
        Self {
            real: 1.0,
            imaginary: 0.0
        }
    }
}

impl Signed for Complex {
    fn abs(&self) -> Self {
        Self {
            real: self.magnitude(),
            imaginary: 0.0
        }
    }

    fn flip(&mut self) {
        *self = *self * -1.0;
    }
}
