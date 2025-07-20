FROM nixos/nix

RUN echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf
RUN echo "sandbox = false" >> /etc/nix/nix.conf

RUN nix profile install nixpkgs#direnv

RUN echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
RUN echo "alias pl='dotnet /Fest-artifact/Fest/Bld/Drops/Release/Binaries/net8.0/p.dll'" >> ~/.bashrc

WORKDIR /Fest-artifact

COPY . /Fest-artifact/

RUN direnv allow /Fest-artifact
RUN cd /Fest-artifact && \
    export NIX_BUILD_SHELL=/bin/bash && \
    nix develop --impure --no-write-lock-file --option sandbox false --command bash -c "./Fest/Bld/build.sh"


WORKDIR /Fest-artifact
CMD ["bash"]
