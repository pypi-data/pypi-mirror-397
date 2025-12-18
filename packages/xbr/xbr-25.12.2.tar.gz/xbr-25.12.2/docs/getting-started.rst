Getting Started
===============

This guide will help you get started with **XBR** for decentralized
data trading and service microtransactions.

Prerequisites
-------------

Before you begin, ensure you have:

* Python 3.9 or later installed
* wamp-xbr installed (see :doc:`installation`)
* Basic familiarity with WAMP and Ethereum concepts

Understanding XBR
-----------------

XBR (Cross-Bar Resource) is a protocol for:

* Secure peer-to-peer data trading
* Service microtransactions in Open Data Markets
* Monetization of data and data-driven microservices

XBR builds on top of WAMP messaging and Ethereum smart contracts.

Basic Concepts
--------------

**Data Markets**
    Open marketplaces where data providers and consumers can trade

**Channels**
    Payment channels for off-chain microtransactions

**Domains**
    Logical groupings of data markets

**Membership**
    Participant registration in data markets

FAQ
---

**What Blockchain options do I have?**

* **Local Development Network**: For testing and development
* **Public Ethereum Networks**: Mainnet and testnets
* **Infura**: Managed Ethereum node service
* **QuikNode**: High-performance dedicated nodes (https://quiknode.io/)
* **Running your own Node**: We recommend `Go Ethereum ("geth") <https://geth.ethereum.org/>`__

For a full geth node on a testnet, minimum requirements are:

* 4GB RAM, 50GB disk (e.g. AWS EC2 ``t3.medium``)
* Full sync time: approximately 4 hours

**Why run your own (public) Ethereum node?**

* Avoid queues to public/shared nodes during high-traffic periods
* Higher chance of transactions being mined quickly
* Event monitors for customized block explorers need complete transaction logs
* Queue and cache batches of transactions

**What are the gas costs for XBR operations?**

Gas costs vary based on network conditions. See the XBR documentation for
current estimates.

**How to resolve MetaMask error "tx doesn't have the correct nonce"?**

If running a test blockchain that was restarted from blank state, MetaMask
caches information about the network including completed transactions.
Clear this cache by selecting a different network in MetaMask or reinstalling.

Next Steps
----------

* Read the :doc:`overview` for a deeper understanding of XBR
* Explore the :doc:`dev/index` for development information
* Check the :doc:`project/index` for project setup guides
* See the :doc:`xbr-cli` for command-line tools
