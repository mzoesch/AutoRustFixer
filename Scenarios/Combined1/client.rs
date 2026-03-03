mod client_lib
{

struct Vector {
    x: f64,
    pub y: f64,
    z: f64,
    w: f64,
}

fn foo(v1: &Vector, v2: &Vector) -> f64
{
    v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w
}

fn bar(v: &Vector) -> f64
{
    foo(v, v).sqrt()
}

mod nested
{

pub fn public_my_nested_bar() -> i32
{
    42
}

fn private_nested_foo() -> i32
{
    42
}

} /* ~mod nested */

pub mod public_nested
{

pub fn public_my_public_nested_bar_different_name() -> i32
{
    42
}

fn my_private_public_foo_different_name() -> i32
{
    42
}

} /* ~mod public_nested */

} /* ~mod client_lib */

fn main()
{
    library::bar(&library::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
    library::math::bar(&library::math::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
    client_lib::bar(&client_lib::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0});
    println!("{}", public_my_nested_bar());
    println!("{}", public_my_public_nested_bar_different_name());
    println!("{}", private_nested_foo());
    println!("{}", my_private_public_foo_different_name());

    return;
}
