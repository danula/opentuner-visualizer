# Opentuner-Visualizer

[![Join the chat at https://gitter.im/danula/opentuner-visualizer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/danula/opentuner-visualizer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

#### Dependencies
Depends on [Bokeh](http://github.com/bokeh/bokeh) library for plotting.
On Ubuntu/Debian run:
```
sudo pip install bokeh django
```

Intall via conda:
```
conda install bokeh django
``` 
### Run
- Start the bokeh-server (`bokeh_server`)
- Run the django server (`python manage.py runserver`)
- Go to [http://localhost:8000](http://localhost:8000)

To save the manipulator file, a helper function is given below
```Python
def save_manipulator(m):
  import pickle
  with open("manipulator", "w") as f:
    f.write(pickle.dumps(m))

def load_manipulator():
  import pickle
  with open("manipulator", "r") as f:
    return pickle.loads(f.read())
  return None
  ```
