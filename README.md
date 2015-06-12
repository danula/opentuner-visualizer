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
- Add the database url to `constants.py`
- Run the django server (`python manage.py runserver`)
- Go to [http://localhost:8000](http://localhost:8000)
