# wf-cli
[![Build Status](https://travis-ci.com/jlchamaa/wf_cli.svg?branch=master)](https://travis-ci.com/jlchamaa/wf_cli)

## What
An open-source notetaking tool that takes much of its core design from the wonderful [workflowy.com](https://www.workflowy.com).  Infinite plaintext notes, stored in an infinitely deep heirarchical structure.  Initially designed with the command line in mind, but written modularly, so that new views can be created on top of the same backend structure.

## Why
Workflowy is wonderful, but for real command line folks, the fact that it lives in the browser and is always in EDIT mode are two design points that make it suboptimal for the command line workflow.  This project is an attempt to make a flavor of workflowy that is designed for command line users to take advantage of features that command line users love, in addtion to other modest improvements.

## Features (All still WIP)
- Separate normal and edit modes, with vim keybindings.  Quicker navigation, search, and editting.
- Note clones.  Breaking the pure tree structure and allowing the same note to belong to both the day and to it's project.  
  - Time-aware notes.  
  - Smart per project tracking.  
- Save notes anywhere, locally or in the cloud, in flat data files that keep track of the nodes and their relationships, rather than ingraining the relationship into a complex and large nested dictionary structure.
- Open source and extensible, can be tuned to anybody's workflow.
- More still to come.
