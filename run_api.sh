#!/bin/bash
#echo "Hello, world!"

export PATH="/root/miniconda3/bin:$PATH"
which python
cd CN_EN_qa/;
#py36;
/root/miniconda3/envs/DrQA/bin/python manage.py runserver 0.0.0.0:5000;
