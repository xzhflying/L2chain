# L2chain
This repository is the code base of the paper titled in "L2chain: Towards High-performance, Confidential and Secure Layer-2 Blockchain Solution for Decentralized Applications".

It aims to implement a proof-of-concept prototype of the proposed layer-2 architecture. Specifically, the **simulator** under the `scripts/` folder provides a comprehensive process simulation by breaking down the main workflows, which provides the evaluations in the paper.

This repository will be updated continuously, aiming to provide an end-to-end solution under the proposed architecture.

## Prepare dependencies 
Environment requirements: Ubuntu 18.04/20.04 LTS, Rust 1.6, Python 3.8

Install SGX driver by running `sudo ./scripts/install_sgx_driver.sh`. For more reference please refer to the [official document](https://download.01.org/intel-sgx/sgx-dcap/1.11/linux/docs/Intel_SGX_SW_Installation_Guide_for_Linux.pdf).

For simulator:
```
cd scripts/simulator
pip install -r requirements.txt
sudo apt install python3-dev
cd enclaves & make
```
Make sure the RSA accumulator implementation from [https://github.com/oleiba/RSA-accumulator](https://github.com/oleiba/RSA-accumulator) is in the ``scripts/simulator`` directory. Meanwhile, the Python shared library is required. To install it on Ubuntu:
``sudo apt install python3-dev``

**References:**

Raft:
python implementation [https://github.com/bakwc/PySyncObj](https://github.com/bakwc/PySyncObj)

RSA_accumulator: 
python implementation [https://github.com/oleiba/RSA-accumulator](https://github.com/oleiba/RSA-accumulator)

Rust implementation [https://github.com/cambrian/accumulator](https://github.com/cambrian/accumulator)

Rust Blockchain (in developing...):
[https://github.com/hkbudb/slimchain](https://github.com/hkbudb/slimchain)

## YCSB workload
To get the YCSB workloads files, please visit https://github.com/brianfrankcooper/YCSB
1. ``cd workloads/ycsb``
2. Download the latest release of YCSB.
3. (On Linux) run ``download_ycsb/bin/ycsb.sh run basic -P download_ycsb/workloads/workloada >> workloada.txt`` (where workloada can be replaced by other workloads)
Then you can get text files contatining fileds like:
> UPDATE usertable \<user\> [ field="\<value\>" ]
> 
> READ usertable \<user\> [ \<all fields\>]
