mod library;

fn main() {
    library::bar(&library::Vector{x: 1.0, y: 2.0, z: 3.0, w: 4.0, a: 5.0, b: 6.0, c: 7.0});
}
