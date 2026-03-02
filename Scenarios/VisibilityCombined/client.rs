mod library;

mod library2
{

struct Vector {
    x: f64,
    pub y: f64,
    z: f64,
    w: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64 {
    v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w
}

fn bar(v: &Vector) -> f64 {
    foo(v, v).sqrt()
}

} /* ~mod library2 */

fn main() {
    library::bar(&library::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
    library::math::bar(&library::math::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
    library2::bar(&library2::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
}
