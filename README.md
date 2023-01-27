# Percona-QA/package-testing
Automated Percona Packaging Testing (GPLv2 Licensed)

# Credits & Ownership
Created by: Hrvoje Matijakovic, Percona

Expanded by: Tomislav Plavcic, Percona

Current Ownership: Tomislav Plavcic

## Execute tests
Tests can be launched locally via vagrant. Please see corresponding Vagrant.template    
* PMM2 deb: [Vagrantfile.template.pmm2-deb](Vagrantfile.template.pmm2-deb)
* PMM2 rpm: [Vagrantfile.template.pmm2-rpm](Vagrantfile.template.pmm2-rpm)

## Developer notes
### Important!
Windows users make sure to ignore file mode in repo due to open defect.
Use: `git config core.fileMode false`

Make sure any script(.sh) has +x byte committed to repo.  
Use `git update-index --chmod=+x myScript.sh` then commit and push.
