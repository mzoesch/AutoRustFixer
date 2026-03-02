pub struct Vector {
    x: f64,
    y: f64,
    z: f64,
    w: f64,
    a: f64,
    b: f64,
    c: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64 {
    v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w + v1.a * v2.a + v1.b * v2.b + v1.c * v2.c
}

pub fn bar(v: &Vector) -> f64 {
    foo(v, v).sqrt()
}
