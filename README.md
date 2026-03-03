# Auto Rust Fixer
This project leverages Rust compiler error messages and feedback from the `rust-analyzer` tool to automatically fix common errors in LLM-produced erroneous Rust code by automatically applying fixes recommended by the Rust framework or by searching all provided code for common mistake patterns. 

# Getting up and running
- Setup environment with Docker (only run **once**; on the **first launch**):
    ```bash 
    docker build -t arf .
    ```
- Launch interactive docker console:
    ```bash 
    docker run -it -v .:/host arf
    ```
- Try to fix compiler errors:
  ```bash
  python3 ./Launch.py \
    -f <path_to_erroneous_file>
  ```

Erroneous examples which the program can handle, can be found under `Scenarios`.
