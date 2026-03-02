struct Vector {
    pub x: f64,
    y: f64,
    z: f64,
    w: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64 {
    v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w
}

fn bar(v: &Vector) -> f64 {
    foo(v, v).sqrt()
}

mod math
{

struct Vector {
    x: f64,
    y: f64,
    z: f64,
    w: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64 {
    v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w
}

fn bar(v: &Vector) -> f64 {
    foo(v, v).sqrt()
}

} /* ~mod math */
