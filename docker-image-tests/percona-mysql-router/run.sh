#!/usr/bin/env bash
pytest -v --junit-xml report.xml $@
