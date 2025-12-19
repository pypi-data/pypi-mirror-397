use core::f64;

use crate::vec3d::Vec3d;

/// A plane in 3D space
#[cfg_attr(feature = "serde", derive(serde::Deserialize, serde::Serialize))]
#[cfg_attr(
    feature = "rkyv",
    derive(rkyv::Deserialize, rkyv::Serialize, rkyv::Archive)
)]
#[derive(Copy, Clone, Debug)]
pub struct Plane {
    /// The normal vector of the plane
    pub normal: Vec3d,
    /// The distance from the origin to the plane
    pub distance: f64
}

impl Plane {
    /// Create a new plane from a normal and the distance from the origin
    pub fn new(normal: &Vec3d, distance: f64) -> Plane {
        Plane {
            normal: normal.normalize(),
            distance: -distance
        }
    }

    /// Create a new plane from a normal and a point on the plane
    /// The normal points outward from the origin
    pub fn from_point(normal: &Vec3d, point: &Vec3d) -> Plane {
        let normal = normal.normalize();
        Plane {
            normal,
            distance: -normal.dot(point)
        }
    }

    /// The XY plane
    pub fn xy() -> Plane {
        Plane::new(&Vec3d::k(), 0.0)
    }

    /// The XZ plane
    pub fn xz() -> Plane {
        Plane::new(&Vec3d::j(), 0.0)
    }

    /// The YZ plane
    pub fn yz() -> Plane {
        Plane::new(&Vec3d::i(), 0.0)
    }

    /// Create a plane from three points
    pub fn from_points(point1: &Vec3d, point2: &Vec3d, point3: &Vec3d) -> Plane {
        let normal = (point2 - point1).cross(&(point3 - point1));
        Plane::from_point(&normal, point1)
    }

    /// Get the unsigned distance from a point to the plane
    pub fn distance_to_point(&self, point: &Vec3d) -> f64 {
        (self.normal.dot(point) + self.distance).abs()
        // self.normal.x * point.x + self.normal.y * point.y + self.normal.z * point.z + self.distance
    }

    /// Get the signed distance from a point to the plane
    pub fn signed_distance_to_point(&self, point: &Vec3d) -> f64 {
        self.normal.dot(point) + self.distance
    }

    /// Calculate if a point lies on the plane
    pub fn contains_point(&self, point: &Vec3d) -> bool {
        self.distance_to_point(point) < f64::EPSILON
    }
}

impl PartialEq for Plane {
    fn eq(&self, other: &Self) -> bool {
        if self.normal == other.normal {
            self.distance == other.distance
        } else if self.normal == -other.normal {
            self.distance == -other.distance
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use assert_float_eq::assert_f64_near;
    use pretty_assertions::assert_eq;

    use super::*;
    use crate::angle::AngleRadians;
    use crate::vec3d::Vec3d;

    #[test]
    fn test_new() {
        let plane = Plane::new(&Vec3d::i(), 5.0);
        assert_f64_near!(plane.distance, -5.0);
        assert_eq!(plane.normal, Vec3d::i());
    }

    #[test]
    fn test_from_point() {
        let point = Vec3d::k();
        let plane = Plane::from_point(&Vec3d::j(), &point);
        let good = Plane::new(&Vec3d::j(), 0.0);
        assert_eq!(plane, good);
    }

    #[test]
    fn test_xy_yz_xz() {
        assert_eq!(Plane::xy(), Plane::new(&Vec3d::k(), 0.0));
        assert_eq!(Plane::xz(), Plane::new(&Vec3d::j(), 0.0));
        assert_eq!(Plane::yz(), Plane::new(&Vec3d::i(), 0.0));
    }

    #[test]
    fn test_from_points() {
        let v1 = Vec3d::zero();
        let v2 = Vec3d::j();
        let v3 = Vec3d::i();
        let plane = Plane::from_points(&v1, &v2, &v3);
        let good = Plane::new(&Vec3d::k(), 0.0);
        assert_eq!(plane, good);
    }

    #[test]
    fn test_distance_to_point() {
        let plane = Plane::xy();
        let v1 = Vec3d::i();
        let v2 = Vec3d::k();
        let v3 = Vec3d::new(3.0, -56.0, -5.0);
        assert_f64_near!(plane.distance_to_point(&v1), 0.0);
        assert_f64_near!(plane.distance_to_point(&v2), 1.0);
        assert_f64_near!(plane.signed_distance_to_point(&v3), -5.0);
        let v = Vec3d::new(1.0, 1.0, 0.0);
        let plane = Plane::new(&v, 1.0);
        let v1 = Vec3d::zero();
        let v2 = Vec3d::new(
            (AngleRadians::quarter_pi() + AngleRadians::half_pi()).cos(),
            (AngleRadians::quarter_pi() + AngleRadians::half_pi()).sin(),
            0.0
        );
        assert_f64_near!(plane.distance_to_point(&v1), 1.0);
        assert_f64_near!(plane.signed_distance_to_point(&v2), -1.0);
        let v = Vec3d::new(1.0, 1.0, 0.0);
        let plane = Plane::new(&v, 1.0);
        assert!(plane.distance_to_point(&v.normalize()) < 1.0e-15);
    }

    #[test]
    #[allow(clippy::similar_names)]
    fn test_distance_to_point_extended() {
        // Plane parallel to YZ (Normal = X) offset by 10
        let plane_yz = Plane::new(&Vec3d::i(), 10.0);
        assert_f64_near!(plane_yz.distance_to_point(&Vec3d::new(10.0, 5.0, 5.0)), 0.0);
        assert_f64_near!(plane_yz.distance_to_point(&Vec3d::new(15.0, 0.0, 0.0)), 5.0);
        assert_f64_near!(
            plane_yz.signed_distance_to_point(&Vec3d::new(0.0, 0.0, 0.0)),
            -10.0
        );

        // Diagonal Plane (45 degrees in XY)
        // Normal points toward (1, 1, 0), Plane passes through origin (d=0)
        let diag_norm = Vec3d::new(1.0, 1.0, 0.0).normalize();
        let plane_diag = Plane::new(&diag_norm, 0.0);

        // Point on the plane
        assert_f64_near!(
            plane_diag.distance_to_point(&Vec3d::new(1.0, -1.0, 10.0)),
            0.0
        );
        // Point along the normal
        assert_f64_near!(
            plane_diag.signed_distance_to_point(&Vec3d::new(1.0, 1.0, 0.0)),
            2.0_f64.sqrt()
        );
        // Point behind the plane
        assert_f64_near!(
            plane_diag.signed_distance_to_point(&Vec3d::new(-1.0, -1.0, 0.0)),
            -2.0_f64.sqrt()
        );

        // Test with a point very far away
        let plane_xz = Plane::new(&Vec3d::j(), 0.0);
        let far_point = Vec3d::new(1e6, -500.0, -1e6);
        assert_f64_near!(plane_xz.signed_distance_to_point(&far_point), -500.0);

        // Test inverted normal
        // Same physical plane as Plane::xy(), but normal points down
        let plane_inv = Plane::new(&Vec3d::new(0.0, 0.0, -1.0), 0.0);
        let top_point = Vec3d::new(0.0, 0.0, 10.0);
        // Distance is now negative because it's "behind" the inverted normal
        assert_f64_near!(plane_inv.signed_distance_to_point(&top_point), -10.0);

        // Arbitrary normalized direction
        let custom_norm = Vec3d::new(1.0, 2.0, 2.0).normalize();
        let plane_custom = Plane::new(&custom_norm, 5.0);
        // The point (custom_norm * 5) is exactly on the plane
        let point_on_plane = custom_norm * 5.0;
        assert!(plane_custom.distance_to_point(&point_on_plane) < 1.0e-15);
        // Origin should be -5.0 from this plane
        assert_f64_near!(plane_custom.signed_distance_to_point(&Vec3d::zero()), -5.0);
    }

    #[test]
    fn test_contains_point() {
        let plane = Plane::xz();
        let v1 = Vec3d::i();
        let v2 = Vec3d::j();
        let v3 = Vec3d::k();
        assert_eq!(plane.contains_point(&v1), true);
        assert_eq!(plane.contains_point(&v2), false);
        assert_eq!(plane.contains_point(&v3), true);
    }
}
