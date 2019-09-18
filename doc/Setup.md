# Setup

For deus we use python3 and a virtual environmoment.

```shell
python3 -m venv venv
source venv/bin/activate
```

For working with geodata we also need gdal.
On ubuntu you can install it using apt:

```shell
sudo apt-get install libgdal20


Then you have to install the dependencies:
```
pip install -r requirements.txt
```

Now you should be able to run the tests:

```python
python3 test_all.py
```

All the tests should pass.

You now can go one with an [example run]{RunExample.md} or read [how deus works]{HowDoesItWorks.md}.
