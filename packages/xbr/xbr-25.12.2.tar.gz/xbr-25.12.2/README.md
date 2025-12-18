# wamp-xbr

[![PyPI](https://img.shields.io/pypi/v/xbr.svg)](https://pypi.python.org/pypi/xbr)
[![Python](https://img.shields.io/pypi/pyversions/xbr.svg)](https://pypi.python.org/pypi/xbr)
[![CI](https://github.com/wamp-proto/wamp-xbr/workflows/main/badge.svg)](https://github.com/wamp-proto/wamp-xbr/actions?query=workflow%3Amain)
[![Docs](https://readthedocs.org/projects/xbr/badge/?version=latest)](https://xbr.readthedocs.io/en/latest/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wamp-proto/wamp-xbr/blob/master/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/xbr.svg)](https://pypi.python.org/pypi/xbr)

------------------------------------------------------------------------

**XBR** enables secure decentralized application messaging, peer-to-peer data-trading and -service microtransactions in open data markets between multiple independent entities or operators.

XBR as a protocol sits on top of [WAMP](https://wamp-proto.org), an open
messaging middleware and service mesh technology, and enables secure
integration, trusted sharing and monetization of data and data-driven
microservices between different parties and users.

The XBR Protocol specification is openly developed and freely usable.

The protocol is implemented in *smart contracts* written in
[Solidity](https://solidity.readthedocs.io) and open-source licensed
([Apache
2.0](https://github.com/crossbario/xbr-protocol/blob/master/LICENSE)).
Smart contracts are designed to run on the [Ethereum
blockchain](https://ethereum.org/). All source code for the XBR smart
contracts is developed and hosted in the project main [GitHub
repository](https://github.com/crossbario/xbr-protocol).

The XBR Protocol and reference documentation can be found
[here](https://s3.eu-central-1.amazonaws.com/xbr.foundation/docs/protocol/index.html).

## Contract addresses

Contract addresses for local development on Ganache, using the

``` console
export XBR_HDWALLET_SEED="myth like bonus scare over problem client lizard pioneer submit female collect"
```

which result in the following contract addresses (when the deployment is
the very first transactions on Ganache):

``` console
export XBR_DEBUG_TOKEN_ADDR=0xCfEB869F69431e42cdB54A4F4f105C19C080A601
export XBR_DEBUG_NETWORK_ADDR=0xC89Ce4735882C9F0f0FE26686c53074E09B0D550
export XBR_DEBUG_MARKET_ADDR=0x9561C133DD8580860B6b7E504bC5Aa500f0f06a7
export XBR_DEBUG_CATALOG_ADDR=0xD833215cBcc3f914bD1C9ece3EE7BF8B14f841bb
export XBR_DEBUG_CHANNEL_ADDR=0xe982E462b094850F12AF94d21D470e21bE9D0E9C
```

## Application development

The XBR smart contracts primary build artifacts are the [contract ABIs
JSON files](https://github.com/crossbario/xbr-protocol/tree/master/abi).
The ABI files are built during compiling the [contract
sources](https://github.com/crossbario/xbr-protocol/tree/master/contracts).
Technically, the ABI files are all you need to interact and talk to the
XBR smart contracts deployed to a blockchain from any (client side)
language or run-time that supports Ethereum, such as
[web3.js](https://web3js.readthedocs.io) or
[web3.py](https://web3py.readthedocs.io).

However, this approach (using the raw XBR ABI files directly from a
\"generic\" Ethereum client library) can be cumbersome and error prone
to maintain. An alternative way is using a client library with built-in
XBR support.

The XBR project currently maintains the following **XBR-enabled client
libraries**:

-   [XBR (contract ABIs package)](https://pypi.org/project/xbr/) for
    Python
-   [Autobahn\|Python](https://github.com/crossbario/autobahn-python)
    for Python (uses the XBR package)
-   [Autobahn\|JavaScript](https://github.com/crossbario/autobahn-js)
    for JavaScript, in browser and NodeJS
-   [Autobahn\|Java](https://github.com/crossbario/autobahn-java) (*beta
    XBR support*) for Java on Android and Java 8 / Netty
-   [Autobahn\|C++](https://github.com/crossbario/autobahn-cpp) (*XBR
    support planned*) for C++ 11+ and Boost/ASIO

XBR support can be added to any [WAMP client
library](https://wamp-proto.org/implementations.html#libraries) with a
language run-time that has packages for Ethereum application
development.

## Build and Release

### Ethereum

To build and release the XBR contracts on Ethereum (Rinkeby), set your
`XBR_HDWALLET_SEED` and run:

``` console
export XBR_HDWALLET_SEED="uncover current ...
make clean compile deploy_rinkeby
```

### Documentation

To build and publish the [XBR contracts
documentation](https://xbr.network/docs/protocol/index.html):

``` console
pip install -r requirements-dev.txt
make clean docs publish_docs
```

### Docker

The following is for building our development blockchain Docker image,
which contains Ganache with the XBR smart contracts already deployed
into, and with initial balances for testaccounts (both ETH and XBR).

The deploying user account 0 becomes contracts owner, and the user is
derived from a seedphrase read from an env var:

``` console
export XBR_HDWALLET_SEED="myth like bonus scare over problem client lizard pioneer submit female collect"
```

The resulting contract addresses, which must be used by XBR clients:

``` console
export XBR_DEBUG_TOKEN_ADDR=0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B
export XBR_DEBUG_NETWORK_ADDR=0xC89Ce4735882C9F0f0FE26686c53074E09B0D550
```

The Docker images are published to:

-   [public](https://hub.docker.com/r/crossbario/crossbarfx-blockchain)
-   [admin](https://hub.docker.com/repository/docker/crossbario/crossbarfx-blockchain)

#### Building the Docker Image

Clean file staging area to create blockchain docker image and run a
blockchain from the empty staging area:

``` console
make clean_ganache run_ganache
```

Compile XBR contracts, deploy to the blockchain and initialize
blockchain data

``` console
make compile deploy_ganache init_ganache
```

Now stop the blockchina, and build the Docker image using the
initialized data from the staging area, and publish the image:

``` console
make build_ganache_docker publish_ganache_docker:
```

### Python

To build and release the XBR contract ABIs Python package **xbr**:

``` console
make clean compile build_python publish_python
```

::: note
::: title
Note
:::

In general, the Python package should have the same version as the XBR
contracts tagged and deployed. Also the ABI bundle archives (ZIP files)
should be in-sync to the former as well.
:::
