mod library
{

mod nested
{

fn foo() -> i32 {
    42
}

} /* ~mod nested */

} /* ~mod library */

fn main()
{
    println!("{}", nested::foo());
}
