## Installing WOFpy (Single or Multi)

**In this example, `Little Bear River MySQL` and `SQLite ODM2` were used.**

These notes cover installation of `WOFpy` from its `conda`; downloading and installing the Little Bear River (LBR) ODM2 MySQL and SQLite test databases; configuring WOFpy for the LBR databases; and running WOFpy. *The instructions enable the creation of "live" web services exposed to external use.* 

Most of the steps were originally copied from [WOFpyODM2LBRtest_installation_notes.md](https://github.com/ODM2/WOFpy/blob/master/docs/WOFpyODM2LBRtest_installation_notes.md) with some modifications; we're no longer actively maintaining that page, but it still has useful content, including references to relevant discussions.

### Testing Environments

We tested WOFpy installations on Amazon Web Services.
Deployment of WOFpy was done in an Ubuntu Server version 16.04. WOFpy is served by using [NGINX](https://www.nginx.com/) and [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/). **The instructions below assume that Amazon AWS EC2 Instance is already set up.**

### [Amazon Web Services (AWS)](https://aws.amazon.com/) 

Note that this installation is currently (2017-3-1) [live on the cloud](http://52.40.105.124:8080/odm2timeseries/). It will be kept live only during active testing, and will be taken down without prior notice when active testing is over. It will be reactivated in the future as needed.

Specifications:
- Ubuntu 16.04
- MySQL 5.6
- NGINX 1.10.2

The AWS Ubuntu Server is running [Systemd init](http://www.freedesktop.org/wiki/Software/systemd/) system.

-----------------

## Table of Contents

<!-- MarkdownTOC depth=3 autolink="true" bracket="round" -->

- [Install Databases](#install-databases)
    - [Installing the LBR ODM2 MySQL test database](#installing-the-lbr-odm2-mysql-test-database)
    - [Downloading the LBR ODM2 SQLite test database](#downloading-the-lbr-odm2-sqlite-test-database)
- [Install WOFpy](#install-wofpy)
- [Installing NGINX](#installing-nginx)
- [Development WOFpy](#development-wofpy)
    - [Get Configuration Folder](#get-configuration-folder)
    - [Edit Configuration `.cfg` files](#edit-configuration-cfg-files)
    - [Test `.cfg` files](#test-cfg-files)
    - [Set up runserver script](#set-up-runserver-script)
        - [Single Server](#single-server)
        - [Multi Server](#multi-server)
- [Production WOFpy](#production-wofpy)
    - [Get Configuration Folder](#get-configuration-folder-1)
    - [Setup `wsgi.py`](#setup-wsgipy)
    - [Setup upstart script](#setup-upstart-script)
    - [Setup NGINX](#setup-nginx)
- [Checking Live instance of WOFpy](#checking-live-instance-of-wofpy)

<!-- /MarkdownTOC -->

------------------
## Install Databases

### Installing the LBR ODM2 MySQL test database

**Note: Do not use MySQL 5.7. We've identified a problem in MySQL 5.7 with loading from the LBR sample database into a geometry column. MySQL 5.6 and 5.5 have been tested successfully.**


1. Download the Little Bear River (LBR) test MySQL database

	```bash
	wget https://raw.githubusercontent.com/ODM2/ODM2/master/usecases/littlebearriver/sampledatabases/odm2_mysql/LBR_MySQL_SmallExample.sql
	```
2.  If MySQL database was a stand alone in Unix, add to /etc/mysql/my.cnf : `lower_case_table_names = 1` under [mysqld]
3. Create ODM2 database in MySQL. At the bash shell where the LBR SQL file was downloaded: 

    ```bash
    mysql -u root -p odm2 < LBR_MySQL_SmallExample.sql
    ```
4. **NOTE: Sample database is missing featuregeometrywkt in samplingfeatures** In order to make WOFpy work, alter the table by adding featuregeometrywkt column, at the mysql client:

	```sql
	ALTER TABLE samplingfeatures ADD featuregeometrywkt VARCHAR (8000) NULL;
	```

### Downloading the LBR ODM2 SQLite test database

Download the Little Bear River (LBR) test SQLite database from WOFpy test directory

```bash
wget https://github.com/ODM2/WOFpy/raw/master/test/odm2/ODM2.sqlite
```
	
-------------------

## Install WOFpy

1. Install miniconda into the user home directory. `/home/ubuntu/miniconda`
	
	```bash
	url=https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh # Python2
	wget $url -O miniconda.sh
	bash miniconda.sh -b -p $HOME/miniconda
	export PATH=$HOME/miniconda/bin:$PATH
	conda update conda --yes
	```

2. Create the "wofpy" conda environment: 

    ```bash
    conda create -n wofpy -c ODM2 -c conda-forge python=2.7 wofpy
    ```

---------------------
## Installing NGINX

**Note: The installation step for NGINX should be the same for both server on AWS and local**

1. Install nginx into the system

	``` bash
	sudo apt install nginx
	```
    
	`NGINX` automatically start after the installation. You should get a welcome page:
	![nginxhome](./img/nginxhome.png)

	**This welcome page is located in `/var/www/html/`**
    
You can check the status of `NGINX` server by running   
```bash
systemctl status nginx
```

*look for `Active: active (running) since Mon 2017-05-15 14:51:45 UTC; 59min ago`*

-------------------------

## Development WOFpy

The steps below are used to setup WOFpy

### Get Configuration Folder
Retrieve WOFpy configuration scripts and files with `wofpy_config` in your `$HOME` directory.

```bash
wofpy_config wofpyserverdev --mode development
```

*The command above will create a folder called `wofpyserverdev` within your `$HOME` directory*

```
wofpyserverdev
+-- odm2
|   +-- timeseries
```

**Note: Currently the command only provide configurations for ODM2 TimeSeries**

### Edit Configuration `.cfg` files
1. Make a copy of `odm2_config_timeseries.cfg` in the newly created `wofpy` folder, so that we can have separate config file for `MySQL` and `SQLite`.

    ```bash
    cp wofpyserverdev/odm2_config_timeseries.cfg wofpyserverdev/odm2_config_mysql.cfg
    ```
    
2. Rename `odm2_config_timeseries.cfg` to make things clear that this is sqlite configuration by default.

    ```bash
    mv wofpyserverdev/odm2_config_timeseries.cfg wofpyserverdev/odm2_config_sqlite.cfg
    ```
    
3. Edit each `.cfg` file to reflect the correct settings. Example below is for `MySQL` database

    ```ini
    [WOF]
    # Edit this to a name that reflect the db, it will be used in the URL
    Network: MySQLODM2Timeseries 
    # Edit this to same name above
    Vocabulary: MySQLODM2Timeseries
    Menu_Group_Name: ODM2
    # Assumes we are using port 8080
    Service_WSDL: http://127.0.0.1:8080/soap/wateroneflow.wsdl 
    Timezone: 00:00
    TimezoneAbbreviation: GMT
    
    # Testing parameters
    [Default_Params]
    Site: USU-LBR-Mendon
    Variable: USU3
    StartDate: 2007-09-01T00:00:00
    EndDate: 2007-09-01T02:30:00

    [WOF_1_1]
    # Assumes we are using port 8080
    Service_WSDL: http://127.0.0.1:8080/soap/wateroneflow_1_1.wsdl 
    
    # Also Testing parameters (for WOF ver. 1.1)
    [Default_Params_1_1]
    West: -114
    South: 40
    East: -110
    North: 42
    
    # Not needed for multiple server (Production), set for (Development) or comment out to use default path
    # [WOFPY]
    # Templates: ../../../../../wof/apps/templates
    
    # Information about the Database 
    # Avoid using localhost in place of 127.0.0.1 below, to minimize problems
    [Database]
    Connection_String: mysql+mysqldb://username:password:@127.0.0.1:3306/ODM2
    ```

### Test `.cfg` files

To test `.cfg` files run the command below after activating `wofpy` conda environment `source activate wofpy`:

First change to `wofpy` directory
```bash
cd $HOME/wofpyserverdev
```
- MySQL
    ```bash
    python runserver_odm2_timeseries.py --config odm2_config_mysql.cfg
    ```
- SQLite
    ```bash
    python runserver_odm2_timeseries.py --config odm2_config_sqlite.cfg
    ```
    
**If each instance works, we are ready to deploy each database or the two together.**

### Set up runserver script

#### Single Server

1. Edit `runserver_odm2_timeseries.py` within `wofpyserverdev` directory to have your config files.
2. For convenience, rename `runserver_odm2_timeseries.py` to `singlerunserver.py`.
    ```bash
    mv runserver_odm2_timeseries.py singlerunserver.py
    ```

3. Edit `singlerunserver.py` to use the mysql config file.

	```python
	dao = Odm2Dao(get_connection('odm2_config_mysql.cfg'))
	```
3. Test that `singlerunserver.py` will deploy WOFpy. Go to one of the endpoints provided, replacing `127.0.0.1` with your server ipaddress:

    ```bash
	source activate wofpy # first activate the correct conda environment
	python singlerunserver.py
    ...
    Access HTML descriptions of endpoints at 
    http://127.0.0.1:8080/mysqlodm2timeseries/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_1_0/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_1_1/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_2/
    ...
    ```

    You should get a result like below. If so, you have successfully deployed `WOFpy` testing server:
	![wofpy home](./img/wofpyhome.png)

#### Multi Server

1. Edit `runserver_multiple_odm2timeseries.py` within `wofpy` directory to have your config files.
2. For convenience, rename `runserver_multiple_odm2timeseries.py` to `runserver.py`.
    ```bash
    mv runserver_multiple_odm2timeseries.py runserver.py
    ```
3. Test that `runserver.py` will deploy WOFpy. Go to one of the endpoints provided, replacing `127.0.0.1` with your server ipaddress:

    ```bash
	source activate wofpy # first activate the correct conda environment
	python runserver.py
    ...
    Access HTML descriptions of endpoints at 
    http://127.0.0.1:8080/mysqlodm2timeseries/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_1_0/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_1_1/
    http://127.0.0.1:8080/mysqlodm2timeseries/rest_2/
    http://127.0.0.1:8080/sqliteodm2timeseries/
    http://127.0.0.1:8080/sqliteodm2timeseries/rest_1_0/
    http://127.0.0.1:8080/sqliteodm2timeseries/rest_1_1/
    http://127.0.0.1:8080/sqliteodm2timeseries/rest_2/
    ...
    ```

    You should get a result like below. If so, you have successfully deployed `WOFpy` testing server:
	![wofpy home](./img/wofpyhome.png)
    
-----------------------

## Production WOFpy


**Follow the same steps as Test except for the step of getting configuration folder, use production mode instead.**

### Get Configuration Folder

Retrieve WOFpy configuration scripts and files with `wofpy_config` in your `$HOME` directory.

```bash
wofpy_config wofpyserverprod --mode production
```

*The command above will create a folder called `wofpyserverprod` within your `$HOME` directory, this time `production_configs` folder is also added with 5 configuration files*

```
wofpyserverprod
+-- odm2
|   +-- timeseries
+-- production_configs
```

Once that's done, continue with steps in Development and below.
    

### Setup `wsgi.py`

1. Move `wsgi.py` and `wofpy.ini` to the same folder as your `runserver` script. In this example `$HOME/wofpyserverprod/odm2/timeseries/`.

    ```bash
    mv $HOME/wofpyserverprod/production_configs/wsgi.py $HOME/wofpyserverprod/odm2/timeseries/
    mv $HOME/wofpyserverprod/production_configs/wofpy.ini $HOME/wofpyserverprod/odm2/timeseries/
    ```

2. Set the secret key within `wsgi.py` and python interpreter. To create secret key, run commands below in `python`

    ```bash
    python
    ```
    
    ```python
    >>> import os
    >>> os.urandom(24).encode('hex')
     'cd48e1c22de0961d5d1bfb14f8a66e006cfb1cfbf3f0c0f3'
    ```
    
    Copy and paste result into `wsgi.py`
    
    ```python
    #! /home/ubuntu/miniconda/envs/wofpy/bin/python
    from singlerunserver import app as application # from runserver for multiserver setup
    application.secret_key = 'cd48e1c22de0961d5d1bfb14f8a66e006cfb1cfbf3f0c0f3'
    ```
    
3. Testing uWSGI with WSGI. Do this by passing name of entry point, specify socket, and protocol (make sure that wofpy conda environment is still active). Go to one of the previous endpoints on your browser once it is deployed.

	``` bash
	uwsgi --socket 0.0.0.0:8080 --protocol=http -w wsgi
	```
	
4. If everything works, now deactivate the conda environment. `$ source deactivate`
5. Stage WOFpy for Production.
    - Move `$HOME/wofpy` folder to `/var/www/` and change user and group to `www-data` so that nginx can read and write to it.
        
        ```bash
        sudo mv $HOME/wofpyserverprod/odm2/timeseries/ /var/www/wofpy/
        sudo chown -R www-data:www-data /var/www/wofpy
        ```
        
6. Enhance Security for WOFpy.     
    - Move `.cfg` files to some private directory. In this example, it is moved to `wofpy_prod` in `$HOME` folder. **THIS IS HIGHLY RECOMMENDED**
        
        ```bash
        mkdir $HOME/wofpy_prod
        sudo mv /var/www/wofpy/*.cfg /home/ubuntu/wofpy_prod/
        ```
        
    - Edit `runserver.py` to use the new path (MultiServer).
        
        ```python
        M_CONFIG_FILE = os.path.join('/home/ubuntu', 'wofpy_prod', 'odm2_config_mysql.cfg')
        S_CONFIG_FILE = os.path.join('/home/ubuntu', 'wofpy_prod','odm2_config_sqlite.cfg')
        ```
        
    - Edit `singlerunserver.py` to use the new path (SingleServer).
        
        ```python
        dao = Odm2Dao(get_connection(os.path.join('/home/ubuntu', 'wofpy_prod', 'odm2_config_mysql.cfg')))
        ```

### Setup upstart script

1. Move the upstart script `$HOME/production_configs/wofpy.service` to `/etc/systemd/system/`. 

    ```bash
    sudo mv $HOME/wofpyserverprod/production_configs/wofpy.service /etc/systemd/system/
    ```

2. Edit ExecStart to match your file paths:

	```ini
	ExecStart=/bin/bash -c 'export PATH=$HOME/miniconda/bin:$PATH; source activate wofpy; cd /var/www/wofpy; uwsgi --ini wofpy.ini'
	```

3. Start the service by using the following command.

	```bash
	sudo systemctl start wofpy
	systemctl status wofpy # This command is to make sure the service is started and running correctly
	sudo systemctl enable wofpy # This command enables the code to run independently
	```

### Setup NGINX

1. Move the server block configuration `$HOME/production_configs/wofpy` to `/etc/nginx/sites-available/`.
    ```bash
    sudo mv $HOME/wofpyserverprod/production_configs/wofpy /etc/nginx/sites-available/
    ```

2. Edit the server block configuration file to match the endpoints. `http://127.0.0.1:8080/mysqlodm2timeseries/` and `http://127.0.0.1:8080/sqliteodm2timeseries/`

	``` bash
	location /mysqlodm2timeseries {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/wofpy/wofpy.sock;
    }
    
    # Leave out the configuration below for (SingleServer)
    location /sqliteodm2timeseries {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/wofpy/wofpy.sock;
    }
	```

3. Enable the Nginx server block configuration by linking the file to the sites-enabled directory.

	```bash
	sudo ln -s /etc/nginx/sites-available/wofpy /etc/nginx/sites-enabled
	```

4. Test for syntax errors in the block config 

	```bash
	sudo nginx -t
	```

    To view nginx errors checkout the log `/var/log/nginx/error.log`.

5. After setting up nginx run the following command
    
    ```bash
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    ```

## Checking Live instance of WOFpy

Go to `ip:8080/mysqlodm2timeseries` and `ip:8080/sqliteodm2timeseries`, *just `ip:8080/mysqlodm2timeseries` for (SingleServer)*. You should see WOFpy running. Click on the links available to see if the application is working properly.
