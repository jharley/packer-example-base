An example base image
=====================

This Packer build example is intended to illustrate building a base image from the official Ubuntu "Xenial" 16.04 AMI from Canonical, and provisioning it using Packer's [ansible Provisioner](https://www.packer.io/docs/provisioners/ansible.html). The build AMI is then launched and tested with [TestInfra](https://testinfra.readthedocs.io).

This is the sibling repository of the Ansible role [ansible-example-base](https://github.com/jharley/ansible-example-base)
