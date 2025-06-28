# db-CBS: Discontinuity-Bounded Conflict-Based Search for Multi-Robot Kinodynamic Motion Planning
Db-CBS is a multi-robot kinodynamic motion planner that enables a team of robots with different dynamics, actuation limits, and shapes to reach their goals in challenging environments.
It solves this problem by combining the Multi-Agent Path Finding (MAPF) optimal solver Conflict-Based Search (CBS), the single-robot kinodynamic motion planner discontinuity-bounded A* (db-A*), and non- linear trajectory optimization.

Paper on [arXiv](https://arxiv.org/abs/2309.16445) and [Video](https://youtu.be/1mglNQOmOLE) are available.


<img align="center" src="https://github.com/IMRCLab/db-CBS/assets/70643834/d371f288-00ec-443b-a5bc-8a79425fde0b" width="70%"/>



<!-- Robot dynamics such as unicycle, $2^{nd}$ order unicycle, double integrator, and car with trailer are implemented in this repository.  -->

## Get primitives

The primitives are on the TUB cloud. The easiest is to use a symlink:

```
ln -s /home/${USER}/tubCloud/projects/db-cbs/motions motions
```

Alternatively, download a copy

```
wget https://tubcloud.tu-berlin.de/s/CijbRaJadf6JwH3/download
unzip download
rm download
```

## Dependencies

The following requirements must be installed on the system in order to build (list is not exhaustive, there might be more, that I currently already have installed but didn't do so specifically for db-CBS):

```
# Boost
sudo apt install libboost-all-dev

# Eigen
sudo apt install libeigen3-dev

# YAML C++
sudo apt install libyaml-cpp-dev

# FCL (Flexible Collision Library)
sudo apt install libfcl-dev

# OMPL (Open Motion Planning Library)
# Needs to be compiled from source. Visit: https://ompl.kavrakilab.org/installation.html
# And download the current installation script from the "From Source" section.
# Don't forget to make the downloaded script executable:
# (While in, e.g., ~/Downloads:)
chmod u+x install-ompl-ubuntu.sh
# Then, run with sudo (without sudo it might fail to install python bindings)
# (In, e.g., ~/Downloads again:)
sudo ./install-ompl-ubuntu.sh --python

# msgpack (Message Pack for C / C++)
sudo apt install libmsgpack-dev

# Crocoddyl (Contact Robot Optimal Control by Differential Dynamic Library)
sudo tee /etc/apt/sources.list.d/robotpkg.list <<EOF
deb [arch=amd64] http://robotpkg.openrobots.org/packages/debian/pub $(lsb_release -sc) robotpkg
EOF

curl http://robotpkg.openrobots.org/packages/debian/robotpkg.key | sudo apt-key add -
sudo apt update
sudo apt install robotpkg-py3\*-crocoddyl

# Move the following into .bashrc or your respective shell to set environment variables.
# YOU MAY NEED TO CHANGE THE PYTHON PATH! Check via ls /opt/openrobots/lib and look for the python3.XX directory
export PATH=/opt/openrobots/bin:$PATH
export PKG_CONFIG_PATH=/opt/openrobots/lib/pkgconfig:$PKG_CONFIG_PATH
export LD_LIBRARY_PATH=/opt/openrobots/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/opt/openrobots/lib/python3.12/site-packages:$PYTHONPATH

# LZ4 (Fast lossless compression algorithm)
sudo apt install liblz4-dev

# Open Dynamics Engine (ODE)
sudo apt install libode-dev
```

To run the benchmark script it is additionally necessary to satisfy the following requirements for your python environment. (Here, using a dedicated virtual environment as system level doesn't work without risking breaking packages.)

```
# TQDM
pip install tqdm

# PSUtil
pip install psutil

# Matplotlib
pip install matplotlib

# Iteration Utilities
pip install iteration_utilities

# YAML
pip install pyyaml

# PDF Crop
pip install pdf-crop

# ------------------------------------
# The following are required for S2M2
# ------------------------------------
# Polytope
pip install polytope

# Gurobi
pip install gurobipy

# Pypoman
sudo apt-get install cython3 libglpk-dev python3 python3-dev python3-pip
sudo apt install install libcdd-dev libgmp-dev
pip install pycddlib
pip install pypoman

# Shapely
pip install shapely

# And probably even more.
```


## Building

(Make sure to satisfy the above dependencies.)
Tested on Ubuntu 24.04.2 LTS

```
mkdir buildRelease
cd buildRelease
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="/opt/openrobots/" ..
make -j
```

## Running

```
cd buildRelease
python3 ../scripts/benchmark.py
```

## ROS
ROS2 workspace needs to have [crazyswarm2](https://github.com/IMRCLab/crazyswarm2).

**Set Up**

Add a symlink of dbcbs_ros to your ROS2 workspace

```
ln <PATH-TO>/dbcbs_ros <PATH-TO>ros2_ws/src/ -s
```

**Build**

```
colcon build --symlink-install
```

**Usage**

Note that all configuration files are the ones used in cvmrs_ros/config. This allows to commit those files without changing the default value of the (public) crazyswarm2 repository.

```
ros2 launch dbcbs_ros launch.py
```

and in a separate terminal

```
ros2 run dbcbs_ros multi_trajectory