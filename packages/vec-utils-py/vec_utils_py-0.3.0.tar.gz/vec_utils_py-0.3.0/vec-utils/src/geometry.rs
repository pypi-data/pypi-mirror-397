/// Circles
pub mod circle;
/// Intersections
/// Only available with std until <https://github.com/rust-lang/rust/issues/137578> gets merged
#[cfg(feature = "std")]
pub mod intersection;
/// Planes
pub mod plane;
/// Spheres
pub mod sphere;
