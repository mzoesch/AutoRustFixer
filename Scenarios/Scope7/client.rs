mod library
{

pub mod nested
{

pub fn foo() -> i32
{
    42
}

} /* ~nested nested */

} /* ~mod library */

fn main()
{
    println!("{}", foo());
}
