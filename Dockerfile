FROM archlinux:latest

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python rustup base-devel

ENV PATH="/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin:${PATH}"

RUN rustup default stable
RUN rustup update
RUN rustup component add rust-analyzer

RUN echo "alias ll='ls -las'" >> ~/.bashrc

WORKDIR /host

CMD ["/bin/bash"]
