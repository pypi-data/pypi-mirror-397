#![no_std]
#![warn(clippy::pedantic)]
#![deny(
    missing_docs,
    clippy::undocumented_unsafe_blocks,
    clippy::unnecessary_safety_doc
)]
#![allow(
    clippy::must_use_candidate,
    clippy::many_single_char_names,
    clippy::return_self_not_must_use,
    clippy::derive_ord_xor_partial_ord,
    incomplete_features
)]
#![cfg_attr(not(feature = "std"), feature(core_float_math))]
#![cfg_attr(feature = "matrix", feature(generic_const_exprs))]
#![doc(test(attr(deny(dead_code))))]
//! A crate for 3D vector, quaternion, geometry, and matrix operations
//! plus some miscellaneous other common things.
//! This library is not focused on performance although improvements are planned

#[cfg(feature = "std")]
#[macro_use]
extern crate std;

/// Angles and angle conversions
pub mod angle;
/// Complex number operations and functions
pub mod complex;
/// 3d geometry operations and functions
pub mod geometry;
/// Internal macros
pub(crate) mod macros;
/// Matrix operations and functions.
/// Requires the "matrix" feature
#[cfg(feature = "matrix")]
pub mod matrix;
/// Quaternion operations and functions
pub mod quat;
/// 3D vector operations and functions
pub mod vec3d;
