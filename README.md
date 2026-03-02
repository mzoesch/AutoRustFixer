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
