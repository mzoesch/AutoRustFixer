pub struct Vector {
    x: f64,
    y: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64 {
    v1.x * v2.x + v1.y * v2.y
}

pub fn bar(v: &Vector) -> f64 {
    foo(v, v).sqrt()
}
