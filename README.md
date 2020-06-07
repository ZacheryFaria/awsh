# Installation

`pip install -U .`


# Setup

First step is to setup your aws credentials

`awsh --configure`

You can also set AWSH_KEY environment variable to the path of your private key that you wish to use to access the instances.

`export AWSH_KEY=/path/to/key.pem`

If you do not set this environment variable you must provide a key with -i

#### View all instances

`awsh --ls`

#### SSH into an instance

`awsh InstanceName`

or

`awsh -i /path/to/key.pem InstanceName`

You can also use the value from the idx column of the --ls command in place of the instance name

`awsh 0`

#### Copy/Execute scripts on instance

All arguments following the instance name will be treated as files to be copied to the instance,
they will be put into the /home/ubuntu directory, preserving name. The first file will be executed
on the machine. All scripts will be executed with sudo privledges. They will be executed implicitly,
so you need the shebang at the top of the file.

`awsh InstanceName script.sh`

or

`awsh InstanceName script.sh somefile.txt`

If you want to just copy the file, use the -c flag

`awsh InstanceName -c somefile.txt anotherfile.txt` 
