# Log Report

This is a simple reporting tool displaying summary statistics about the content of a 
database. The tool works as a command-line application. It was created as part of Udacity's Full-Stack Nanodegree to 
showcase the use of SQL.

### Prerequisites

* [Vagrant](https://www.vagrantup.com/): It's used to setup the development environment.


### Installing

Start by launching a console and cd-ing to the location of this repository.

1. Create the virtual machine. Beforehand, make sure that the [Vagrantfile](./Vagrantfile) is present in the 
directory. Then type `vagrant up`.

2. SSH into the machine with `vagrant ssh`, then `cd /vagrant/`

3. The kind folks at Udacity have already installed all the dependencies we need. All we're left to do is seeding the 
database. to do that run `psql -d news -f newsdata.sql`

4. Last step ! Now we need to create some supporting views into our news database. To do that, run `./log_report.py 
--create_views`

You're all set.

## Usage

To get the help type `./log_report.py -h`.

The application will display three lists of information answering the following questions:
1. _What are the most popular **n** articles of all time?_
    
    To select **n**, use the option `--n` on the application. For example, to get the top five: `./log_report.py --n 5`
    
2. _Who are the most popular article authors of all time?_

3. _On which days did more than **x**% of requests lead to errors?_

    To select the x, use `--p`. For example, to select 0.5%, type: `./log_report.py --p 0.005`
    
## Known Issue
if you're running the vagrant box from a Windows machine, calling the script using `./log_report.py` may fail due to 
DOS line endings. to solve the issue do the following inside your box:
```
sudo apt-get update
sudo apt-get install dos2unix
dos2unix log_report.py
```