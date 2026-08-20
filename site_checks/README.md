# Testing the availability of various MySQL packages/tarballs on the main site

## PS (full PS version needed)
### 8.0 or innovation 8.X
```
docker run --env PS_VER_FULL=8.0.34-26.1 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_ps.py"
```
### 5.7
```
docker run --env PS_VER_FULL=5.7.44-48.1 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_ps.py"
```
## PDPS (full PS, PXB, orchestartor versions needed + PT, proxysql versions)
### 8.0 or innovation 8.X
```
docker run --env PS_VER_FULL=8.0.34-26.1 --env PXB_VER_FULL=8.0.34-29.1 --env ORCH_VER_FULL=3.2.6-10 --env PT_VER=3.5.4 --env PROXYSQL_VER=2.5.5 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pdps.py"
```
## PXC (full PXC version needed; PXC57_INNODB mandatory for PXC57)
### 8.0 or innovation 8.X
```
docker run --env PXC_VER_FULL=8.0.34-26.1 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pxc.py"
```
### 5.7
```
docker run --env PXC_VER_FULL=5.7.43-31.65.1 --env PXC57_INNODB=47 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pxc.py"
```
## PDPXC (full PXC, PXB versions needed + PT, proxysql, haproxy, replication manager versions)
### 8.0 or innovation 8.X
```
docker run --env PXC_VER_FULL=8.0.34-26.1 --env PXB_VER_FULL=8.0.34-29.1 --env PT_VER=3.5.5 --env PROXYSQL_VER=2.5.5 --env HAPROXY_VER=2.8.1 --env REPL_MAN_VER=1.0 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pdpxc.py"
```
## PXB (full PXB version needed)
### 8.0 or innovation 8.X
```
docker run --env PXB_VER_FULL=8.0.34-29.1 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pxb.py"
```
### 2.4
```
docker run --env PXB_VER_FULL=2.4.28-1 --rm -v `pwd`:/tmp -w /tmp python bash -c "pip3 install requests pytest setuptools && env && pytest -s --junitxml=junit.xml test_pxb.py"
```

